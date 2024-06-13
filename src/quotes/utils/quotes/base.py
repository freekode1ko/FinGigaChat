"""Модуль с набором иструментов для работы с источниками данных"""
import datetime
from abc import ABC, abstractmethod
from typing import Any, Tuple, Union

import pandas as pd
import requests as req
from sqlalchemy import text

import module.crawler as crawler
import module.data_transformer as dt
from configs import config
from db import database


class QuotesGetter(ABC):
    """Класс для получения источников данных"""

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
        """Вынимает из ссылки на источник название страницы (кусок url от самого левого /)"""
        return tables_row[3].rstrip('/').rsplit('/', 1)[-1]

    def get_tables(self, session: req.sessions.Session) -> list:
        """
        Получает по источнику подгруппы котировок таблицы и возвращает список источников с собранными для них таблицами.

        :param session: Сессия для выполнения HTTP-запросов.
        :return: Список источников и собранных для них таблиц.
        """
        all_tables = []
        group_name = self.get_group_name()
        query = (
            f'SELECT sg.name, p.id, p.response_format, p.source '
            f'FROM parser_source p '
            f'JOIN source_group sg ON p.source_group_id = sg.id '
            f"WHERE sg.name_latin='{group_name}'"
        )
        df_urls = pd.read_sql(query, con=database.engine)
        urls = df_urls.values.tolist()
        for url in urls:
            euro_standard, page_html = self.parser_obj.get_html(url[3], session)
            try:
                tables = self.transformer_obj.get_table_from_html(euro_standard, page_html)
                all_tables.extend([[*url, table] for table in tables])  # alias, id, block, source
                self.logger.info(f'Таблиц добавлено ({group_name}): {len(tables)}')
            except ValueError as val_err:
                self.logger.error(f'Таблицы не найдены ({group_name}). {val_err}: {page_html[:100]}')
            except Exception as e:
                self.logger.error(f'Ошибка при поиске таблицы ({group_name}) {url[-1]}: {e}')
        return all_tables

    def save_date_of_last_build(self) -> None:
        """Старый функционал"""
        group_name = self.get_group_name()
        cur_time = datetime.datetime.now().strftime(config.BASE_DATETIME_FORMAT)
        cur_time_in_box = pd.DataFrame([[cur_time]], columns=['date_time'])
        cur_time_in_box.to_sql('date_of_last_build', if_exists='replace', index=False, con=database.engine)
        self.logger.info(f'Таблица date_of_last_build записана ({group_name})')

    def save_last_time_update(self, sources_ids: set):
        """Обновляет время сбора данных с источников sources_ids"""
        group_name = self.get_group_name()
        with database.engine.connect() as conn:
            query = text(
                'UPDATE parser_source '
                'SET previous_update_datetime=last_update_datetime, last_update_datetime=CURRENT_TIMESTAMP '
                'WHERE id = ANY(:sources_ids)'
            )
            conn.execute(query.bindparams(sources_ids=list(sources_ids)))
            conn.commit()
        self.logger.info(f'Обновлено время сборки котировок ({group_name})')

    @staticmethod
    def get_extra_data() -> list:
        """Используется, если нужно получить источники, которые были отброшены на этапе get_tables"""
        return []

    @classmethod
    def get_group_name(cls) -> str:
        """Возвращает имя группы котировок"""
        return cls.NAME

    @staticmethod
    @abstractmethod
    def filter(table_row: list) -> bool:
        """Используется для отбора данных из ТЗ.xlsx"""
        pass

    @abstractmethod
    def preprocess(self, tables: list, session: req.sessions.Session) -> Tuple[Any, set]:
        """
        Основная функция сбора информации с источников

        :param tables: Таблицы, собранные с источников данных по котировкам
        :param session: requests Сессия
        :return: Кортеж из результата, для сохранения и множества id источников, с которых удалось собрать данные
        """
        pass

    def save(self, data: Union[pd.DataFrame, Any]) -> None:
        """Сохраняет собранные данные по котировкам"""
        group_name = self.get_group_name()
        data.to_sql(group_name, if_exists='replace', index=False, con=database.engine)
        self.logger.info(f'Таблица {group_name} записана')

    def collect(self) -> None:
        """Собирает данные по котировкам с источников"""
        group_name = self.get_group_name()
        session = req.Session()
        all_tables = self.get_tables(session)
        self.logger.info(f'Котировки ({group_name}) собраны, запускаем обработку')

        if extra_data := self.get_extra_data():
            all_tables.append(extra_data)

        data, preprocessed_ids = self.preprocess(all_tables, session)
        self.save(data)
        self.save_last_time_update(preprocessed_ids)

    def find_number(self, name: str, data_list: list[str], bloom: bool = False) -> float | None:
        """
        Находит первое число в списке.

        :param name:        Название котировки.
        :param data_list:   Список из спаршенных элементов.
        :param bloom:       Является ли источник блумбергом.
        :return:            Первое число в списке (значение котировки).
        """
        end = 20
        data_list = [el.replace(',', '') for el in data_list[:end]] if bloom else data_list[:end]
        for item in data_list:
            try:
                return float(item)
            except ValueError:
                pass
        self.logger.info('Не было найдено число при парсинге котировки %s' % name)
        return None
