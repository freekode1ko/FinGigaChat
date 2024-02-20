from sqlalchemy import text

import database


def update_get_datetime(source_name: str, source_link: str) -> None:
    """
    Обновялет время сбора данных research с источника

    :param source_name: Имя собираемых данных
    :param source_link: Ссылка, где данные собираются
    """
    query = text(
        'UPDATE research_source '
        'SET previous_update_datetime=llast_update_datetime, last_update_datetime=CURRENT_TIMESTAMP '
        'WHERE name=:source_name AND source=:source_link;'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(source_name=source_name, source_link=source_link))
        conn.commit()
