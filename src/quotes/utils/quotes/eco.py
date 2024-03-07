from typing import Tuple, List

import pandas as pd
import requests as req

from db import database
from utils.quotes.base import QuotesGetter


class EcoGetter(QuotesGetter):
    NAME = 'eco'

    world_bet_columns: List[str] = ['Country', 'Last', 'Previous', 'Reference', 'Unit']
    rus_infl_columns: List[str] = ['Дата', 'Ключевая ставка, % годовых', 'Инфляция, % г/г', 'Цель по инфляции, %']

    @staticmethod
    def filter(table_row: list) -> bool:
        page = QuotesGetter.get_source_page_from_table_row(table_row)
        pages = ['KeyRate', 'ruonia', 'interest-rate', 'infl']
        return table_row[0] == 'Экономика' and page in pages

    def economic_block(self, table_eco: list, page_eco: str):
        eco_frst_third = []
        world_bet = pd.DataFrame(columns=self.world_bet_columns)
        rus_infl = pd.DataFrame(columns=self.rus_infl_columns)
        if page_eco == 'KeyRate':
            eco_frst_third.append(['Текущая ключевая ставка Банка России', table_eco[4]['Ставка'][0]])
            self.logger.info('Таблица Экономика (KeyRate) собрана')

        elif page_eco == 'ruonia':
            ruonia = table_eco[4].loc[table_eco[4][0] == 'Ставка RUONIA, %'][2].values.tolist()[0]
            eco_frst_third.append(['Текущая ставка RUONIA', ruonia])
            self.logger.info('Таблица Экономика (ruonia) собрана')

        elif page_eco == 'interest-rate':
            if 'Actual' in table_eco[4] and 'Unit' in table_eco[4]:
                eco_frst_third.append(['LPR Китай', table_eco[4]['Actual'][0]])
                self.logger.info('Таблица interest-rate (LPR Китай) собрана')

            elif 'Country' in table_eco[4]:
                world_bet = pd.concat([world_bet, table_eco[4]])
                self.logger.info('Таблица interest-rate (Country) собрана')

        elif page_eco == 'infl':
            rus_infl = pd.concat([rus_infl, table_eco[4]])
            self.logger.info('Таблица Экономика (infl) собрана')

        return eco_frst_third, world_bet, rus_infl

    def preprocess(self, tables: list, session: req.sessions.Session) -> Tuple[Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame], set]:
        preprocessed_ids = set()
        group_name = self.get_group_name()
        eco_frst_third = []
        world_bet = pd.DataFrame(columns=self.world_bet_columns)
        rus_infl = pd.DataFrame(columns=self.rus_infl_columns)

        size_tables = len(tables)
        self.logger.info(f'Обработка собранных таблиц ({group_name}) ({size_tables}).')
        for enum, tables_row in enumerate(tables, 1):
            self.logger.info(f'{group_name} {enum}/{size_tables}')
            source_page = self.get_source_page_from_table_row(tables_row)
            self.logger.info(f'Сборка таблицы {source_page} из блока {tables_row[0]} ({group_name})')

            # ECONOMIC BLOCK
            try:
                eco_list, world_bet_df, rus_infl_df = self.economic_block(tables_row, source_page)
                eco_frst_third += eco_list
                world_bet = pd.concat([world_bet, world_bet_df])
                rus_infl = pd.concat([rus_infl, rus_infl_df])
                preprocessed_ids.add(tables_row[1])
            except Exception as e:
                self.logger.error(f'При обработке источника {tables_row[3]} ({group_name}) произошла ошибка: %s', e)

        eco_stake = pd.DataFrame(eco_frst_third)
        return (eco_stake, world_bet, rus_infl), preprocessed_ids

    def save(self, data: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]) -> None:
        eco_stake, world_bet, rus_infl = data

        eco_stake.to_sql('eco_stake', if_exists='replace', index=False, con=database.engine)
        self.logger.info('Таблица eco_stake записана')
        world_bet.to_sql('eco_global_stake', if_exists='replace', index=False, con=database.engine)
        self.logger.info('Таблица eco_global_stake записана')
        rus_infl.to_sql('eco_rus_influence', if_exists='replace', index=False, con=database.engine)
        self.logger.info('Таблица eco_rus_influence записана')
