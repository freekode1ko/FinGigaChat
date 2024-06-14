"""Модуль для получения и обработки данных по металлам (сырью/комодам)."""
import re

import pandas as pd
import requests as req
from lxml import html
from sqlalchemy import text

from configs import config
from db import database
from utils.quotes.base import QuotesGetter


class MetalsGetter(QuotesGetter):
    """Класс для получения и обработки данных по металлам (сырью/комодам)."""

    NAME = 'metals'

    LBS_IN_T = 2204.62  # фунты в тонны
    # словарь с информацией о таблицах и коммодах, которые собрались с tradingeconomics
    TRADING_DATA_TABLE: dict[str, dict] = config.tradingeconomics_commodities['tables']

    big_table_columns: list[str] = ['Metals', 'Price', 'Day', '%', 'Weekly', 'Monthly', 'YoY', 'Date']
    middle_table_columns: list[str] = ['Metals', 'Price', 'Weekly', 'Date']
    small_table_columns: list[str] = ['Metals', 'Price']

    # TODO: ненужно? + удалить из parser_source
    @staticmethod
    def get_extra_data() -> list:
        """По этим данным не удается получить таблицы стандартным способом"""
        with database.engine.connect() as conn:
            query = text(
                'SELECT sg.name, p.id, p.response_format, p.source '
                'FROM parser_source p '
                'JOIN source_group sg ON p.source_group_id = sg.id '
                'WHERE p.source=:source LIMIT 1'
            )
            source = 'https://www.bloomberg.com/quote/LMCADS03:COM'
            row = conn.execute(query.bindparams(source=source)).fetchone()

        copper_source = [*row, [pd.DataFrame()]]
        return copper_source

    @staticmethod
    def filter(table_row: list) -> bool:
        """
        Проверяет, является ли строка таблицы строкой с данными по металлам (сырью/комодам).

        :param table_row: Строка таблицы для проверки
        :return: True, если строка содержит данные по металлам (сырью/комодам), False в противном случае.
        """
        page = QuotesGetter.get_source_page_from_table_row(table_row)
        pages = ['LMCADS03:COM', 'U7*0', 'commodities', 'coal-(api2)-cif-ara-futures-historical-data']
        return table_row[0] == 'Металлы' and page in pages

    def metal_block(self,
                    table_metals: list,
                    page_metals: str,
                    session: req.sessions.Session) -> tuple[list, list, list]:
        """
        Собирает из таблиц показатели по коммодам.

        :param table_metals: [имя группы (Металлы), айди из parser_source, response_format из parser_source,
                            url, таблица со страницы html]
        :param page_metals: название страницы
        :param session: сессия
        return: списки с показателями по коммодам
        """
        U7 = []
        metals = []
        metals_from_html = []

        if page_metals == 'U7*0':
            first_col = table_metals[4].columns[0]
            df_last_price = table_metals[4][table_metals[4][first_col] == 'Last Price']
            if not df_last_price.empty:
                price = df_last_price.iloc[0, 1]
                U7.append(['Coking Coal', price])
                self.logger.info('Таблица U7 собрана')

        elif page_metals == 'commodities':
            for table_name, commodities_data in self.TRADING_DATA_TABLE.items():
                if table_name in table_metals[4].columns:
                    temp = table_metals[4].loc[
                        table_metals[4][table_name].isin(
                            [commodity_data['name'] for commodity_data in commodities_data]
                        )
                    ]
                    metals.append(temp.rename(columns={table_name: 'Metals'}))
                    self.logger.info('Таблица metals (%s) собрана' % table_name)

        elif page_metals == 'lng-japan-korea-marker-platts-futures':
            metal_name = 'LNG Japan/Korea'
            url = table_metals[3]
            xpath_price = '//*[@data-test="instrument-price-last"]//text()'
            xpath_date = '//*[@data-test="trading-time-label"]//text()'
            lng = self.get_data_from_page(session, metal_name, url, xpath_price, xpath_date)
            metals_from_html.append(lng)
        elif page_metals == 'LMCADS03:COM':
            metal_name = 'Copper Bloomberg'
            url = table_metals[3]
            xpath_price = '//div[starts-with(@class, "currentPrice")]//div[@data-component="sized-price"]/text()'
            xpath_date = '//time[1]/@datetime'
            lng = self.get_data_from_page(session, metal_name, url, xpath_price, xpath_date, delete_commas=True)
            metals_from_html.append(lng)

        return metals_from_html, metals, U7

    def get_data_from_page(self,
                           session: req.sessions.Session,
                           metal_name: str,
                           url: str,
                           xpath_price: str,
                           xpath_date: str,
                           delete_commas: bool = False,
                           ) -> list[str, float | None, None, str]:
        """
        Получение цены и даты металла с html страницы.

        :param metal_name:      название коммода
        :param url:             ссылка на страницу с данными о коммоде
        :param session:         сессия
        :param xpath_price:     xpath путь до цены коммода
        :param xpath_date:      xpath путь до даты(времени) обновления цены
        :param delete_commas:   нужно ли очищать данные от запятых
        :return:                список с данными по металлу
        """
        useless, page_html = self.parser_obj.get_html(url, session)
        tree = html.fromstring(page_html)
        data_price = tree.xpath(xpath_price)
        price = self.find_number(metal_name, data_price, delete_commas)
        data_date = tree.xpath(xpath_date)
        date = [date for date in data_date if date.strip()][0]
        return [metal_name, price, None, date]

    def preprocess(self, tables: list, session: req.sessions.Session) -> tuple[pd.DataFrame, set]:
        """
        Предобрабатывает таблицы данных и создает итоговый DataFrame с данными по металлам.

        :param tables: Список таблиц данных.
        :param session: Сессия для выполнения HTTP-запросов.
        :return: Кортеж, содержащий DataFrame с данными по металлам и множество идентификаторов обработанных таблиц.
        """
        preprocessed_ids = set()
        group_name = self.get_group_name()
        U7_full, metals_full, metals_from_html_full = [], [], []

        size_tables = len(tables)
        self.logger.info(f'Обработка собранных таблиц ({group_name}) ({size_tables}).')
        for enum, tables_row in enumerate(tables, 1):
            self.logger.info(f'{group_name} {enum}/{size_tables}')
            source_page = self.get_source_page_from_table_row(tables_row)
            self.logger.info(f'Сборка таблицы {source_page} из блока {tables_row[0]} ({group_name})')

            # METALS BLOCK
            try:
                metals_from_html, metals, U7 = self.metal_block(tables_row, source_page, session)
                U7_full += U7
                metals_from_html_full += metals_from_html
                metals_full += metals
                preprocessed_ids.add(tables_row[1])
            except Exception as e:
                self.logger.error(f'При обработке источника {tables_row[3]} ({group_name}) произошла ошибка: %s', e)

        big_table = pd.DataFrame(columns=self.big_table_columns)
        metals_from_html_df = pd.DataFrame(metals_from_html_full, columns=self.middle_table_columns)
        U7_df = pd.DataFrame(U7_full, columns=self.small_table_columns)
        for table in metals_full:
            big_table = pd.concat([big_table, table], ignore_index=True)
        big_table = pd.concat([big_table, metals_from_html_df, U7_df], ignore_index=True)
        big_table = big_table.drop_duplicates(subset='Metals', ignore_index=True)
        # self.from_lbs_to_ton(big_table)
        self.post_process(big_table)
        return big_table, preprocessed_ids

    def from_lbs_to_ton(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Преобразует цену на комоды из фунтов в тонны

        :param df: DataFrame с данными по металлам.
        :return: DataFrame Обновленный DataFrame с преобразованными ценами.
        """
        commodities_in_lbs = [commodity['name']
                              for com_list in self.TRADING_DATA_TABLE.values()
                              for commodity in com_list
                              if re.search('Lbs', commodity['unit'])]
        indexes = df[df['Metals'].isin(commodities_in_lbs)].index
        df.loc[indexes, ['Price', 'Day']] = df.loc[indexes, ['Price', 'Day']] * self.LBS_IN_T
        return df

    def post_process(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Пост обработать цены на коммоды.

        :param df:  Датафрейм с информацией о ценах на коммоды.
        :return:    Обработанный датафрейм.
        """
        # заменить цену меди с tradingeconomics на bloomberg
        df.loc[df['Metals'] == 'Copper USD/Lbs', 'Price'] = df.loc[df['Metals'] == 'Copper Bloomberg', 'Price'].values[0]
        # Перевести цену за уран в тонны
        df.loc[df['Metals'] == 'Uranium USD/Lbs', 'Price'] *= self.LBS_IN_T
        return df
