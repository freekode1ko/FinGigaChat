import datetime

import pandas as pd
import requests as req
from lxml import html
from sqlalchemy import text

from db import database
from utils.quotes.base import QuotesGetter


class MetalsGetter(QuotesGetter):
    NAME = 'metals'

    LBS_IN_T = 2204.62

    big_table_columns: list[str] = ['Metals', 'Price', 'Day', '%', 'Weekly', 'Monthly', 'YoY', 'Date']
    middle_table_columns: list[str] = ['Metals', 'Price', 'Weekly', 'Date']
    small_table_columns: list[str] = ['Metals', 'Price']

    # TODO: ненужно? + удалить из parser_source
    @staticmethod
    def get_extra_data() -> list:
        """По этим данным не удалется получить таблицы стандартным способом"""
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
        page = QuotesGetter.get_source_page_from_table_row(table_row)
        pages = ['LMCADS03:COM', 'U7*0', 'commodities', 'coal-(api2)-cif-ara-futures-historical-data']
        return table_row[0] == 'Металлы' and page in pages

    def metal_block(self, table_metals: list, page_metals: str, session: req.sessions.Session) -> tuple[list, list, list]:
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
            if {'Last', 'Change'}.issubset(table_metals[4].columns):
                y = datetime.date.today().strftime('%y')
                jap_coal_pattern = f'U7(M|N){y}'
                jap_coal = table_metals[4][table_metals[4].Symbol.str.contains(jap_coal_pattern)]
                U7.append(['кокс. уголь', jap_coal.values.tolist()[0][1]])
                self.logger.info('Таблица U7N24 собрана')

        elif page_metals == 'commodities':
            if 'Metals' in table_metals[4].columns:
                temp = table_metals[4].loc[
                    table_metals[4]['Metals'].isin([
                        'Gold USD/t,oz',
                        'Silver USD/t,oz',
                        'Platinum USD/t,oz',
                        'Copper USD/Lbs',
                    ])
                ]
                metals.append(temp)
                self.logger.info('Таблица metals (Metals) собрана')

            elif 'Industrial' in table_metals[4].columns:
                temp = table_metals[4].loc[
                    table_metals[4]['Industrial'].isin(
                        [
                            'Aluminum USD/T',
                            'Nickel USD/T',
                            'Lead USD/T',
                            'Zinc USD/T',
                            'Palladium USD/t,oz',
                            'Cobalt USD/T',
                            'Iron Ore 62% fe USD/T',
                            'Tin USD/T',
                        ]
                    )
                ]
                metals.append(temp.rename(columns={'Industrial': 'Metals'}))
                self.logger.info('Таблица metals (Industrial) собрана')

            elif 'Energy' in table_metals[4].columns:
                temp = table_metals[4].loc[table_metals[4]['Energy'].isin([
                    'Crude Oil USD/Bbl',
                    'Urals Oil USD/Bbl',
                    'Brent USD/Bbl',
                    'Coal USD/T',
                    'Uranium USD/Lbs',
                ])]
                metals.append(temp.rename(columns={'Energy': 'Metals'}))
                self.logger.info('Таблица metals (Energy) собрана')

        elif page_metals == 'lng-japan-korea-marker-platts-futures':
            metal_name = 'LNG Japan/Korea'
            url = table_metals[3]
            xpath_price = '//*[@data-test="instrument-price-last"]//text()'
            xpath_date = '//*[@data-test="trading-time-label"]//text()'
            lng = self.get_data_from_page(session, metal_name, url, xpath_price, xpath_date)
            metals_from_html.append(lng)

        return metals_from_html, metals, U7

    def get_data_from_page(self,
                           session: req.sessions.Session,
                           metal_name: str,
                           url: str,
                           xpath_price: str,
                           xpath_date: str
                           ):
        """
        Получение цены и даты металла с html страницы.

        :param metal_name: название коммода
        :param url: ссылка на страницу с данными о коммоде
        :param session: сессия
        :param xpath_price: xpath путь до цены коммода
        :param xpath_date: xpath путь до даты(времени) обновления цены
        """
        useless, page_html = self.parser_obj.get_html(url, session)
        tree = html.fromstring(page_html)
        data_price = tree.xpath(xpath_price)
        price = self.find_number(data_price)
        data_date = tree.xpath(xpath_date)
        date = [date for date in data_date if date.strip()][0]
        return [metal_name, price, None, date]

    def preprocess(self, tables: list, session: req.sessions.Session) -> tuple[pd.DataFrame, set]:
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

        # преобразование фунтов в тонны
        index = big_table[big_table['Metals'] == 'Copper USD/Lbs'].index[0]
        big_table.loc[index, 'Price'] *= self.LBS_IN_T

        return big_table, preprocessed_ids
