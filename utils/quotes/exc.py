import datetime
from typing import Tuple, List

import pandas as pd
import requests as req
from lxml import html

import database
from utils.quotes.base import QuotesGetter


class ExcGetter(QuotesGetter):
    NAME = 'exc'

    fx_columns: List[str] = ['Валюта', 'Курс']

    @staticmethod
    def find_number(data_list):
        """Находит первое число в списке"""
        for item in data_list[:20]:
            try:
                return float(item)
            except ValueError:
                pass
        return None

    @staticmethod
    def filter(table_row: list) -> bool:
        page = QuotesGetter.get_source_page_from_table_row(table_row)
        pages = ['usd-rub', 'eur-rub', 'cny-rub', 'eur-usd', 'usd-cnh', 'usdollar']
        return table_row[0] == 'Курсы валют' and page in pages

    def exchange_block(self, table_exchange: list, exchange_page: str, session: req.sessions.Session):
        exchange_kot = []
        if exchange_page in ['usd-rub', 'eur-rub', 'cny-rub', 'eur-usd']:
            if exchange_page == 'usd-rub':
                euro_standard, page_html = self.parser_obj.get_html(table_exchange[3], session)
                tables = pd.read_html(page_html)
                for table in tables:
                    try:
                        exchange_table = table[table.Exchange.str.startswith('Real-time Currencies')]
                        if not exchange_table.empty:
                            row = ['usd-rub', exchange_table['Last'].values[0]]
                            exchange_kot.append(row)
                            self.logger.info('Таблица exchange_kot (usd-rub) собрана')
                            break
                    except IndexError:
                        self.logger.warning('Не та таблица попала на обработку')
                    except Exception as ex:
                        self.logger.error(f'Ошибка при обработке таблицы: {ex}')
            elif {'Exchange', 'Last', 'Time'}.issubset(table_exchange[4].columns):
                row = [
                    exchange_page,
                    table_exchange[4].loc[table_exchange[4].Exchange.str.startswith('Real-time Currencies')]['Last'].values.tolist()[0],
                ]
                exchange_kot.append(row)
                self.logger.info('Таблица exchange_kot (Exchange) собрана')

        elif exchange_page in ['usd-cnh', 'usdollar']:
            euro_standard, page_html = self.parser_obj.get_html(table_exchange[3], session)
            tree = html.fromstring(page_html)
            data = tree.xpath('//*[@id="__next"]/div[2]/div//text()')
            price = self.find_number(data)
            row = [exchange_page, price]
            exchange_kot.append(row)
            self.logger.info('Таблица exchange_kot (usd-cnh) собрана')
        return exchange_kot

    def preprocess(self, tables: list, session: req.sessions.Session) -> Tuple[pd.DataFrame, set]:
        preprocessed_ids = set()
        group_name = self.get_group_name()
        exchange_kot = []

        size_tables = len(tables)
        self.logger.info(f'Обработка собранных таблиц ({group_name}) ({size_tables}).')
        for enum, tables_row in enumerate(tables, 1):
            self.logger.info(f'{group_name} {enum}/{size_tables}')
            source_page = self.get_source_page_from_table_row(tables_row)
            self.logger.info(f'Сборка таблицы {source_page} из блока {tables_row[0]} ({group_name})')

            # EXCENGE BLOCK
            try:
                exchange_kot += self.exchange_block(tables_row, source_page, session)
                preprocessed_ids.add(tables_row[1])
            except Exception as e:
                self.logger.error(f'При обработке источника {tables_row[3]} ({group_name}) произошла ошибка: %s', e)

        # Запись Курсов в БД и Локальное хранилище
        fx_df = pd.DataFrame(exchange_kot, columns=self.fx_columns).drop_duplicates(subset=['Валюта'],
                                                                                       ignore_index=True)
        return fx_df, preprocessed_ids

    def save(self, data: pd.DataFrame) -> None:
        group_name = self.get_group_name()
        data.to_excel('sources/tables/exc.xlsx', sheet_name='Курсы валют')
        self.logger.info('Записана страница с Курсами')
        # Write to fx DB
        data.to_sql('exc', if_exists='replace', index=False, con=database.engine)
        self.logger.info(f'Таблица {group_name} записана')
