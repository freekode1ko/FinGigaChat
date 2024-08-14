"""Вспомогательные функции при создании call report'ов"""
from datetime import datetime
from typing import Optional

from configs import config


def validate_and_parse_date(date_str: str) -> Optional[datetime.date]:
    """
    Валидация строки с датой и возвращение ее в datetime object

    :param date_str: date str
    :return: Возвращает время в питоновском формате
    """
    try:
        date_obj = datetime.strptime(date_str, config.BASE_DATE_FORMAT)
        return date_obj.date()
    except ValueError:
        return
