"""Запросы к бд связанные с сообщениями"""
import inspect

import pandas as pd
from sqlalchemy import text

from db import database
from db.message_type import message_types


__table_name__ = 'message'


def get_messages_by_type(message_type_id: int):
    """
    Возвращает список id сообщений grouped by user_id с указанным типом message_type_id,которые были отправлены за последние 48 часов

    (https://core.telegram.org/bots/api#deletemessage)

    :param message_type_id: id типа сообщения из таблицы message_type
    return: DataFrame[[user_id: int, message_ids: list[int]]]
    """
    query = (
        f'SELECT user_id, ARRAY_AGG(message_id) as message_ids FROM {__table_name__} '
        f"WHERE {message_type_id=:} AND send_datetime > (CURRENT_TIMESTAMP -  INTERVAL '2 days') "
        f'GROUP BY user_id;'
    )

    return pd.read_sql_query(query, con=database.engine)


def add_message(user_id: int, message_id: int, message_type: str = None, function_name: str = None) -> int:
    """
    Добавляет в БД запись, что пользователю user_id было отправлено сообщение с id = message_id

    :param user_id: telegram user_id
    :param message_id: id отправленного ботом сообщения
    :param message_type: название типа сообщения, если имя типа сообщения None или таковое отстутствует в БД,
                         то в качестве message_type будет использоваться значени по умолчанию
    :param function_name: Имя функции, которая вызвала данный метод, если None, то используется имя вызвавшей функции
                          (при использовании внутри декоратора будет получение имя декоратора, а не изначальной функции)
    return: id созданной записи
    """
    query = text(
        f'INSERT INTO {__table_name__} (user_id, message_id, message_type_id, function_name) '
        f'VALUES (:user_id, :message_id, :message_type_id, :function_name) '
        f'RETURNING id;'
    )

    if function_name is None:
        func = inspect.currentframe().f_back.f_code
        function_name = func.co_name

    try:
        message_type_id = message_types.get_by_name(message_type)['id']
    except (IndexError, KeyError):
        message_type_id = message_types.default['id']

    params = {
        'user_id': user_id,
        'message_id': message_id,
        'message_type_id': message_type_id,
        'function_name': function_name,
    }

    with database.engine.connect() as conn:
        result = conn.execute(query.bindparams(**params)).scalar_one()
        conn.commit()

    return result


def add_all(messages: list[dict], function_name: str = None) -> None:
    """
    Сохраняет в базу все сообщения из списка messages

    :param messages: Список словарей с полями {user_id: int, message_id: int, message_type: str}
    :param function_name: Имя функции, которая вызвала данный метод, если None, то используется имя вызвавшей функции
                          (при использовании внутри декоратора будет получение имя декоратора, а не изначальной функции)
    """
    queries = []
    query = text(
        f'INSERT INTO {__table_name__} (user_id, message_id, message_type_id, function_name) '
        f'VALUES (:user_id, :message_id, :message_type_id, :function_name) '
        f'RETURNING id;'
    )

    if function_name is None:
        func = inspect.currentframe().f_back.f_code
        function_name = func.co_name

    for m in messages:
        try:
            message_type_id = message_types.get_by_name(m['message_type'])['id']
        except (IndexError, KeyError):
            message_type_id = message_types.default['id']
        m = {
            'user_id': m['user_id'],
            'message_id': m['message_id'],
            'message_type_id': message_type_id,
            'function_name': function_name,
        }
        queries.append(query.bindparams(**m))

    with database.engine.connect() as conn:
        for q in queries:
            conn.execute(q)
        conn.commit()


def delete_messages(user_id: int, message_ids: list[int]) -> None:
    """
    Удаляет запись в БД о сообщении, где user_id=user_id AND message_id=message_id

    :param user_id: telegram user_id
    :param message_ids: Список id сообщений
    """
    query = text(f'DELETE FROM {__table_name__} WHERE user_id=:user_id AND message_id = ANY(:message_ids);')

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(user_id=user_id, message_ids=message_ids))
        conn.commit()
