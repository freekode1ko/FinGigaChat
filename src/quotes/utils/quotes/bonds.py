"""Модуль для обработки котировок облигаций."""
from typing import List, Tuple

import pandas as pd
import requests as req

from utils.quotes.base import QuotesGetter


class BondsGetter(QuotesGetter):
    """Класс для получения и обработки данных котировок облигаций."""

    NAME: str = 'bonds'

    bonds_kot_columns: List[str] = ['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время']

    @staticmethod
    def filter(table_row: list) -> bool:
        """
        Проверяет, является ли строка таблицы строкой с данными по облигациям.

        :param table_row: Строка таблицы для проверки.
        :return: True, если строка содержит данные по облигациям, False в противном случае.
        """
        return table_row[0] == 'Облигации' and table_row[2] == 'Блок котировки'

    def bond_block(self, table_bonds: list) -> pd.DataFrame:
        """
        Обрабатывает блок данных по облигациям и создает DataFrame.

        :param table_bonds: Список данных по облигациям.
        :return: DataFrame с обработанными данными по облигациям.
        """
        bonds_kot = pd.DataFrame(columns=self.bonds_kot_columns)
        bonds_kot = pd.concat([bonds_kot, table_bonds[4]])
        self.logger.info(f'Таблица Облигации (Котировки) {table_bonds[3]} собрана')
        return bonds_kot

    def preprocess(self, tables: list, session: req.sessions.Session) -> Tuple[pd.DataFrame, set]:
        """
        Предобрабатывает таблицы данных и создает итоговый DataFrame с котировками облигаций.

        :param tables: Список таблиц данных.
        :param session: Сессия для выполнения HTTP-запросов.
        :return: Кортеж, содержащий DataFrame с данными по облигациям и множество идентификаторов обработанных таблиц.
        """
        preprocessed_ids = set()
        group_name = self.get_group_name()
        bonds_kot = pd.DataFrame(columns=self.bonds_kot_columns)
        size_tables = len(tables)
        self.logger.info(f'Обработка собранных таблиц ({group_name}) ({size_tables}).')
        for enum, tables_row in enumerate(tables, 1):
            self.logger.info(f'{group_name} {enum}/{size_tables}')
            source_page = self.get_source_page_from_table_row(tables_row)
            self.logger.info(f'Сборка таблицы {source_page} из блока {tables_row[0]} ({group_name})')
            # BONDS BLOCK
            try:
                bonds_kot = pd.concat([bonds_kot, self.bond_block(tables_row)])
                preprocessed_ids.add(tables_row[1])
            except Exception as e:
                self.logger.error(f'При обработке источника {tables_row[3]} ({group_name}) произошла ошибка: %s', e)
        return bonds_kot, preprocessed_ids
