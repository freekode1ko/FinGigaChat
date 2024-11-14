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
        model = ParserUpdateLastUpdateTime if request_type == RequestType.update else ParserCreate
        logger.info('Форматирование данных')
        data['name'] = data['name'].astype(str)
        res = []
        for i, row in data.iterrows():
            d = row.to_dict()
            if d.get('last_update_datetime'):
                d['last_update_datetime'] = cls._convert_datetime_to_utc_tz(d['last_update_datetime'])
            res.append(model(**d))
        logger.info('Данные отформатированы')
        return res
