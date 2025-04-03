"""Модуль форматирования статусов парсеров"""
from datetime import timedelta

import pandas as pd

from constants.enums import RequestType
from db.db_tz import get_db_timezone, get_delta_hours
from log.logger_base import logger
from schemas.parser import ParserCreate, ParserUpdateLastUpdateTime


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class ParserFormatter:
    """Класс форматирования статусов парсеров"""

    @staticmethod
    def _convert_lud_to_moscow_tz(data: pd.DataFrame) -> pd.DataFrame:
        """
        Форматирование времени последнего обновления в зону Europe/Moscow.

        :param data:    Датафрейм с данными парсеров.
        :return:         Датафрейм с отформатированной датой.
        """
        if 'last_update_datetime' not in data.columns:
            return data

        logger.info('Преобразование дат в московское время')
        data = data.copy().dropna(subset=['last_update_datetime'])
        db_tz = get_db_timezone()
        delta_hours = timedelta(hours=get_delta_hours(db_tz))
        data['last_update_datetime'] += delta_hours
        return data

    @classmethod
    def format(cls, data: pd.DataFrame, request_type: RequestType) -> list[ParserUpdateLastUpdateTime | ParserCreate]:
        """
        Форматирование даты парсинга.

        (в таблице parser_source все даты должны быть сохранены с помощью current_timestamp или datetime.now())

        :param data:            Датафрейм с данными по парсерам.
        :param request_type:    Тип запроса: на создание или обновление парсера.
        :return:                Список из Pydantic моделей с данными из датафрейма.
        """
        logger.info('Форматирование данных')
        data['name'] = data['name'].astype(str)
        data = cls._convert_lud_to_moscow_tz(data)
        model = ParserUpdateLastUpdateTime if request_type == RequestType.PUT else ParserCreate
        res = [model(**row.dropna()) for _, row in data.iterrows()]
        logger.info('Данные отформатированы')
        return res
