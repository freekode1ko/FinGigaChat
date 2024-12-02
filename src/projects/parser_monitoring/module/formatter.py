"""Модуль форматирования статусов парсеров"""
import time
from datetime import datetime

import pandas as pd

from constants.enums import RequestType
from log.logger_base import logger
from schemas.parser import ParserCreate, ParserUpdateLastUpdateTime


DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class ParserFormatter:
    """Класс форматирования статусов парсеров"""

    @staticmethod
    def _convert_datetime_to_utc_tz(dt: datetime) -> datetime:
        """Перевести время в utc"""
        return datetime.strptime(
            time.strftime(
                DATETIME_FORMAT,
                time.gmtime(
                    time.mktime(
                        time.strptime(
                            dt.strftime(DATETIME_FORMAT),
                            DATETIME_FORMAT,
                        )
                    )
                )
            ),
            DATETIME_FORMAT,
        )

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
        model = ParserUpdateLastUpdateTime if request_type == RequestType.PUT else ParserCreate
        data['name'] = data['name'].astype(str)

        if 'last_update_datetime' in data.columns:
            data = data.dropna(subset=['last_update_datetime'])
            data['last_update_datetime'] = data['last_update_datetime'].apply(lambda lud: cls._convert_datetime_to_utc_tz(lud))

        res = [model(**row.dropna()) for _, row in data.iterrows()]
        logger.info('Данные отформатированы')
        return res
