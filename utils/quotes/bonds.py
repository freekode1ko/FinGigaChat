import datetime

import pandas as pd
import requests as req

import database
from utils.quotes.base import QuotesGetter


class BondsGetter(QuotesGetter):
    NAME = 'bonds'

    @staticmethod
    def filter(table_row: list) -> bool:
        return table_row[0] == 'Облигации' and table_row[2] == 'Блок котировки'

    def bond_block(self, table_bonds: list) -> pd.DataFrame:
        bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])
        bonds_kot = pd.concat([bonds_kot, table_bonds[4]])
        self.logger.info(f'Таблица Облигации (Котировки) {table_bonds[3]} собрана')
        return bonds_kot

    def preprocess(self, tables: list, session: req.sessions.Session) -> pd.DataFrame:
        group_name = self.get_group_name()
        bonds_kot = pd.DataFrame(columns=['Название', 'Доходность', 'Осн,', 'Макс,', 'Мин,', 'Изм,', 'Изм, %', 'Время'])
        size_tables = len(tables)
        self.logger.info(f'Обработка собранных таблиц ({group_name}) ({size_tables}).')
        for enum, tables_row in enumerate(tables, 1):
            self.logger.info(f'{group_name} {enum}/{size_tables}')
            source_page = self.get_source_page_from_table_row(tables_row)
            self.logger.info(f'Сборка таблицы {source_page} из блока {tables_row[0]} ({group_name})')
            # BONDS BLOCK
            bonds_kot = pd.concat([bonds_kot, self.bond_block(tables_row)])
        return bonds_kot

    def save(self, data: pd.DataFrame) -> None:
        group_name = self.get_group_name()
        # Запись Котировок в БД и Локальное хранилище
        data.to_excel('sources/tables/bonds.xlsx', sheet_name='Блок котировки')
        self.logger.info(f'Записана страница с Котировками ({group_name})')
        data.to_sql('bonds', if_exists='replace', index=False, con=database.engine)
        self.logger.info(f'Таблица {group_name} записана')
