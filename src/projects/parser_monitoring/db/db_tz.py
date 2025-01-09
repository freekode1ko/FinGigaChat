"""Работа с TimeZone базы данных."""
from sqlalchemy import text

from configs.config import MOSCOW_TZ, UTC_TZ
from db import database


def get_db_timezone() -> str:
    """Получение timezone базы данных."""
    with database.engine.connect() as conn:
        res = conn.execute(text('show timezone'))
        timezone = res.scalar()
    return timezone


def get_delta_hours(timezone: str) -> int:
    """
    Получение разницы в часах для преобразования времени в московское.

    :param:     timezone базы данных.
    :return:    Часы для преобразования времени в московское.
    """
    if timezone == str(UTC_TZ):
        return 3
    elif timezone == str(MOSCOW_TZ):
        return 0
    raise ValueError(f'Неизвестная временная зона: {timezone}')
