import datetime
from typing import Tuple

import pandas as pd
import requests as req
from dateutil.relativedelta import relativedelta
from lxml import html
from sqlalchemy import text

import database
from utils.quotes.base import QuotesGetter


class MetalsGetter(QuotesGetter):
    NAME = 'metals'

    @staticmethod
    def get_extra_data() -> list:
        with database.engine.connect() as conn:
            query = text('SELECT alias, id, block, source WHERE source=:source LIMIT 1')
            source = 'https://www.bloomberg.com/quote/LMCADS03:COM'
            row = conn.execute(query.bindparams(source=source)).fetchone()

        copper_source = [*row, [pd.DataFrame()]]
        return copper_source

    @staticmethod
    def filter(table_row: list) -> bool:
        page = QuotesGetter.get_source_page_from_table_row(table_row)
        pages = ['LMCADS03:COM', 'U7*0', 'commodities', 'coal-(api2)-cif-ara-futures-historical-data']
        return table_row[0] == 'Металлы' and page in pages

    def metal_block(self, table_metals: list, page_metals: str, session: req.sessions.Session):
        U7N23 = []
        metals_kot = []
        metals_coal_kot = []
        metals_bloom = pd.DataFrame(columns=['Metals', 'Price', 'Day'])

        if page_metals == 'LMCADS03:COM':
            euro_standard, page_html = self.parser_obj.get_html(table_metals[3], session)
            tree = html.fromstring(page_html)
            object_xpath = '//*[@id="__next"]/div/div[2]/div[6]/div/main/div/div[1]/div[4]/div'
            price = tree.xpath('{}/div[1]/text()'.format(object_xpath))
            price_diff = tree.xpath('{}/div[2]/span/span/text()'.format(object_xpath))
            temp_df = pd.DataFrame(columns=['Metals', 'Price', 'Day'])
            try:
                row = ['Медь', price[0], price_diff[0]]
                temp_df = pd.DataFrame([row], columns=['Metals', 'Price', 'Day'])
            except Exception as ex:
                self.logger.error(f'Ошибка ({ex}) получения таблицы с медью!')
            metals_bloom = pd.concat([metals_bloom, temp_df], ignore_index=True)
            self.logger.info('Таблица metals_bloom собрана')

        elif page_metals == 'U7*0':
            if {'Last', 'Change'}.issubset(table_metals[4].columns):
                jap_coal = table_metals[4][table_metals[4].Symbol.str.contains('U7.24')]
                U7N23.append(['кокс. уголь', jap_coal.values.tolist()[0][1]])
                self.logger.info('Таблица U7N24 собрана')

        elif page_metals == 'commodities':
            if 'Metals' in table_metals[4].columns:
                temp = table_metals[4].loc[
                    table_metals[4]['Metals'].isin(['Gold USD/t,oz', 'Silver USD/t,oz', 'Platinum USD/t,oz', 'Lithium CNY/T'])
                ]
                metals_kot.append(temp)
                self.logger.info('Таблица metals_kot (Metals) собрана')

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
                        ]
                    )
                ]
                metals_kot.append(temp.rename(columns={'Industrial': 'Metals'}))
                self.logger.info('Таблица metals_kot (Industrial) собрана')

            elif 'Energy' in table_metals[4].columns:
                temp = table_metals[4].loc[table_metals[4]['Energy'].isin(['Coal USD/T'])]
                metals_kot.append(temp.rename(columns={'Energy': 'Metals'}))
                self.logger.info('Таблица metals_kot (Energy) собрана')

        elif page_metals == 'coal-(api2)-cif-ara-futures-historical-data':
            if 'Price' in table_metals[4].columns:
                table_metals[4]['Date'] = table_metals[4]['Date'].astype('datetime64[ns]')
                # day_day = table_metals[4]['Date'][0] - relativedelta(days=1)
                week_day = table_metals[4]['Date'][0] - relativedelta(weeks=1)
                month_day = table_metals[4]['Date'][0] - relativedelta(months=1)
                year_day = table_metals[4]['Date'][0] - relativedelta(years=1)

                # day_table = table_metals[4].loc[table_metals[4]['Date'] == str(day_day).split()[0]]
                week_table = table_metals[4].loc[table_metals[4]['Date'] == str(week_day).split()[0]]
                month_table = table_metals[4].loc[table_metals[4]['Date'] == str(month_day).split()[0]]
                year_table = table_metals[4].loc[table_metals[4]['Date'] == str(year_day).split()[0]]
                temp_table = pd.concat([table_metals[4].head(1), week_table, month_table, year_table], ignore_index=True)

                temp_table['Metals'] = 'Эн. уголь'
                temp_table['%'] = temp_table.groupby('Metals')['Price'].pct_change()
                temp_table['%'] = temp_table.groupby('Metals')['Price'].pct_change()
                try:
                    metals_coal_kot.append(
                        [
                            temp_table['Metals'][0],
                            temp_table['Price'][0],
                            *temp_table['%'].tolist()[1:],
                            str(temp_table['Date'][0]).split()[0],
                        ]
                    )
                    self.logger.info('Таблица metals_coal_kot собрана')
                except ValueError:
                    metals_coal_kot.append(
                        [
                            temp_table['Metals'][0],
                            temp_table['Price'][0],
                            *temp_table['%'].tolist()[0:],
                            str(temp_table['Date'][0]).split()[0],
                        ]
                    )
                    self.logger.warning('Сдвиг в таблице с котировками (metals_coal_kot)')

        return metals_coal_kot, metals_kot, metals_bloom, U7N23

    def preprocess(self, tables: list, session: req.sessions.Session) -> Tuple[list, list, list, pd.DataFrame]:
        group_name = self.get_group_name()
        U7N23 = []
        metals_kot = []
        metals_coal_kot = []
        metals_bloom = pd.DataFrame(columns=['Metals', 'Price', 'Day'])

        size_tables = len(tables)
        self.logger.info(f'Обработка собранных таблиц ({group_name}) ({size_tables}).')
        for enum, tables_row in enumerate(tables, 1):
            self.logger.info(f'{group_name} {enum}/{size_tables}')
            source_page = self.get_source_page_from_table_row(tables_row)
            self.logger.info(f'Сборка таблицы {source_page} из блока {tables_row[0]} ({group_name})')

            # METALS BLOCK
            metal_coal_ls, metal_cat_ls, metal_bloom_df, U7_ls = self.metal_block(tables_row, source_page, session)
            U7N23 += U7_ls
            metals_coal_kot += metal_coal_ls
            metals_kot += metal_cat_ls
            metals_bloom = pd.concat([metals_bloom, metal_bloom_df])

        return U7N23, metals_kot, metals_coal_kot, metals_bloom

    def save(self, data: Tuple[list, list, list, pd.DataFrame]) -> None:
        group_name = self.get_group_name()
        U7N23, metals_kot, metals_coal_kot, metals_bloom = data

        # Запись Металов и Сырья в БД и Локальное хранилище
        big_table = pd.DataFrame(columns=['Metals', 'Price', 'Day', '%', 'Weekly', 'Monthly', 'YoY', 'Date'])
        metals_coal_kot_table = pd.DataFrame(metals_coal_kot, columns=['Metals', 'Price', 'Weekly', 'Date'])
        U7N23_df = pd.DataFrame(U7N23, columns=['Metals', 'Price'])
        for table in metals_kot:
            big_table = pd.concat([big_table, table], ignore_index=True)
        big_table = pd.concat([big_table, metals_coal_kot_table, metals_bloom, U7N23_df], ignore_index=True)

        big_table.to_excel('sources/tables/metal.xlsx', sheet_name='Металы')
        self.logger.info('Записана страница с Металлами')
        big_table.to_sql('metals', if_exists='replace', index=False, con=database.engine)
        self.logger.info(f'Таблица {group_name} записана')
