"""Модуль для получения и обработки данных обменных курсов."""
from typing import List, Tuple

import pandas as pd
import requests as req
from lxml import html

from utils.quotes.base import QuotesGetter


class ExcGetter(QuotesGetter):
    """Класс для получения и обработки данных об обменных курсах."""

    NAME = 'exc'

    fx_columns: List[str] = ['Валюта', 'Курс']

    @staticmethod
    def filter(table_row: list) -> bool:
        """
        Проверяет, является ли строка таблицы строкой с данными об обменных курсах.

        :param table_row: Строка таблицы для проверки.
        :return: True, если строка содержит данные об обменных курсах, False в противном случае.
        """
        page = QuotesGetter.get_source_page_from_table_row(table_row)
        pages = ['usd-rub', 'eur-rub', 'cny-rub', 'eur-usd', 'usd-cnh', 'usdollar']
        return table_row[0] == 'Курсы валют' and page in pages

    def exchange_block(self, table_exchange: list, exchange_page: str, session: req.sessions.Session) -> list[list]:
        """
        Обрабатывает блок данных об обменных курсах, и создает список данных.

        :param table_exchange: Список данных об обменных курсах.
        :param exchange_page: Тип данных об обменных курсах.
        :param session: Сессия для выполнения HTTP-запросов.
        :return: Список списков с данными об обменных курсах.
        """
        # такой вариант берет число на самом верху страницы, но норм ли?
        # сразу решает проблему актуальности, так как это самые актуальные данные
        # решают проблему юаня
        euro_standard, page_html = self.parser_obj.get_html(table_exchange[3], session)
        tree = html.fromstring(page_html)
        data = tree.xpath('//*[@data-test="instrument-price-last"]//text()')
        price = self.find_number(self.NAME, data)
        return [[exchange_page, price]]

    def preprocess(self, tables: list, session: req.sessions.Session) -> Tuple[pd.DataFrame, set]:
        """
        Предобрабатывает таблицы данных и создает итоговый DataFrame с данными об обменных курсах.

        :param tables: Список таблиц данных.
        :param session: Сессия для выполнения HTTP-запросов.
        :return: Кортеж, содержащий DataFrame с данными об обменных курсах
        и множество идентификаторов обработанных таблиц.
        """
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
        fx_df = pd.DataFrame(exchange_kot, columns=self.fx_columns).drop_duplicates(subset=['Валюта'], ignore_index=True)
        return fx_df, preprocessed_ids
