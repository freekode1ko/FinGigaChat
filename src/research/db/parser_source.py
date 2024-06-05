"""Интерфейс для взаимодействия с таблицами источниками для парсинга"""
import datetime
import json
from typing import Any

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


def get_source_data(source_name: str, column: str) -> Any:
    """
    Метод получения времени сбора данных research с источника

    :param source_name: Имя собираемых данных
    :param column:      Имя столбца БД, данные из которого вынимаются
    :returns:           Значение в колонке column по источнику source_name
    """
    query = text(
        f'SELECT {column} '
        f'FROM {__table_name__} '
        f'WHERE name=:source_name '
        f'LIMIT 1;'
    )

    with database.engine.connect() as conn:
        data = conn.execute(query.bindparams(source_name=source_name)).scalar_one()

    return data


def get_source_last_update_datetime(source_name: str) -> datetime.datetime:
    """
    Метод получения времени сбора данных research с источника

    :param source_name: Имя собираемых данных
    :returns:           Время последней сборки данных с источника source_name
    """
    return get_source_data(source_name, column='last_update_datetime')


def get_source(source_name: str) -> str:
    """
    Метод получения ссылки источника

    :param source_name: Имя собираемых данных
    :returns:           Ссылка на источник
    """
    return get_source_data(source_name, column='source')


def get_research_type_source_by_name(source_name: str) -> dict[str, int | str | dict | list]:
    """
    Метод получения данных из таблицы parser_source по имени источника

    :param source_name: Имя собираемых данных
    :returns:           dict[research_type_id, filepath, header, text, parse_datetime,publication_date,report_id]
    """
    query = text(
        f'SELECT source, params, alt_names, before_link, response_format '
        f'FROM {__table_name__} '
        f'WHERE name=:source_name '
        f'LIMIT 1;'
    )

    with database.engine.connect() as conn:
        data = conn.execute(query.bindparams(source_name=source_name)).fetchone()

        source = {
            'research_type_id': 0,
            'url': data[0],
            'params': json.dumps(data[1]) or '{}',
            'starts_with': data[2],
            'before_link': data[3],
            'request_method': data[4]
        }
        return source
