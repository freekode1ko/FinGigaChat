import datetime

from sqlalchemy import text

from db import database

__table_name__ = 'parser_source'


def update_get_datetime(source_name: str) -> None:
    """
    Обновялет время сбора данных research с источника

    :param source_name: Имя собираемых данных
    """
    query = text(
        f'UPDATE {__table_name__} '
        f'SET previous_update_datetime=last_update_datetime, last_update_datetime=CURRENT_TIMESTAMP '
        f'WHERE name=:source_name;'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(source_name=source_name))
        conn.commit()


def get_source_last_update_datetime(source_name: str) -> datetime.datetime:
    """
    Метод получения времени сбора данных research с источника

    :param source_name: Имя собираемых данных
    :return: datetime
    """
    query = text(
        f'SELECT last_update_datetime '
        f'FROM {__table_name__} '
        f'WHERE name=:source_name '
        f'LIMIT 1;'
    )

    with database.engine.connect() as conn:
        last_update_datetime = conn.execute(query.bindparams(source_name=source_name)).scalar_one()

    return last_update_datetime
