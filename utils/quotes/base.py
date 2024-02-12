import datetime
from abc import ABC, abstractmethod
from typing import Callable, Any

import pandas as pd
import requests as req
from sqlalchemy import text

import config
import database
import module.crawler as crawler
import module.data_transformer as dt


class QuotesGetter(ABC):
    NAME = 'base quotes getter class'

    def __init__(self, logger):
        self.logger = logger
        parser_obj = crawler.Parser(self.logger)
        transformer_obj = dt.Transformer()

        self.engine = database.engine
        self.parser_obj = parser_obj
        self.transformer_obj = transformer_obj

    @staticmethod
    def get_source_page_from_table_row(tables_row: list) -> str:
        parts = tables_row[3].split('/')
        url_index = -1 if parts[-1] else -2
        return parts[url_index]

    def get_tables(self, session: req.sessions.Session, filter_function: Callable[[list], bool] = bool) -> list:
        all_tables = []
        group_name = self.get_group_name()
        # urls = self.transformer_obj.load_urls_as_list(self.path_to_source, 'Источник')
        # df_urls = pd.DataFrame(urls).dropna().drop_duplicates()
        # urls = df_urls.values.tolist()
        query = 'SELECT alias, id, block, source FROM quote_source'
        df_urls = pd.read_sql(query, con=database.engine)
        urls = df_urls.values.tolist()
        for url in urls:
            table_row_prefix_list = [url[0].split('/')[0], *url[1:]]  # alias, id, block, source
            if not filter_function(table_row_prefix_list):
                continue

            euro_standard, page_html = self.parser_obj.get_html(url[3], session)
            try:
                tables = self.transformer_obj.get_table_from_html(euro_standard, page_html)
                all_tables.extend([[*table_row_prefix_list, table] for table in tables])
                self.logger.info(f'Таблиц добавлено ({group_name}): {len(tables)}')
            except ValueError as val_err:
                self.logger.error(f'Таблицы не найдены ({group_name}). {val_err}: {page_html[:100]}')
            except Exception as e:
                self.logger.error(f'Ошибка при поиске таблицы ({group_name}) {url[-1]}: {e}')
        return all_tables

    def save_date_of_last_build(self) -> None:
        group_name = self.get_group_name()
        cur_time = datetime.datetime.now().strftime(config.BASE_DATETIME_FORMAT)
        cur_time_in_box = pd.DataFrame([[cur_time]], columns=['date_time'])
        cur_time_in_box.to_sql('date_of_last_build', if_exists='replace', index=False, con=database.engine)
        self.logger.info(f'Таблица date_of_last_build записана ({group_name})')

    def save_last_time_update(self, sources_ids: set):
        group_name = self.get_group_name()
        with database.engine.connect() as conn:
            query = text('UPDATE quote_source SET last_update_datetime=CURRENT_TIMESTAMP WHERE id = ANY(:sources_ids)')
            conn.execute(query.bindparams(sources_ids=list(sources_ids)))
            conn.commit()
        self.logger.info(f'Обновлено время сборки котировок ({group_name})')

    @staticmethod
    def get_extra_data() -> list:
        return []

    @classmethod
    def get_group_name(cls) -> str:
        return cls.NAME

    @staticmethod
    @abstractmethod
    def filter(table_row: list) -> bool:
        pass

    @abstractmethod
    def preprocess(self, tables: list, session: req.sessions.Session) -> Any:
        pass

    @abstractmethod
    def save(self, data: Any) -> None:
        pass

    def collect(self) -> None:
        group_name = self.get_group_name()
        session = req.Session()
        all_tables = self.get_tables(session, self.filter)
        sources_ids = {i[1] for i in all_tables}
        self.logger.info(f'Котировки ({group_name}) собраны, запускаем обработку')

        if extra_data := self.get_extra_data():
            all_tables.append(extra_data)

        data = self.preprocess(all_tables, session)
        self.save(data)
        self.save_last_time_update(sources_ids)
