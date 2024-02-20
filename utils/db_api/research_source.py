import datetime

from sqlalchemy import text

import database


__table_name__ = 'research_source'


def update_get_datetime(source_name: str, source_link: str) -> None:
    """
    Обновялет время сбора данных research с источника

    :param source_name: Имя собираемых данных
    :param source_link: Ссылка, где данные собираются
    """
    query = text(
        f'UPDATE {__table_name__} '
        f'SET previous_update_datetime=last_update_datetime, last_update_datetime=CURRENT_TIMESTAMP '
        f'WHERE name=:source_name AND source=:source_link;'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(source_name=source_name, source_link=source_link))
        conn.commit()


def get_source_last_update_datetime(source_name: str, source_link: str) -> datetime.datetime:
    """

    """
    query = text(
        f'SELECT last_update_datetime '
        f'FROM {__table_name__} '
        f'WHERE name=:source_name AND source=:source_link '
        f'LIMIT 1;'
    )

    with database.engine.connect() as conn:
        last_update_datetime = conn.execute(query.bindparams(source_name=source_name, source_link=source_link)).scalar_one()

    return last_update_datetime
