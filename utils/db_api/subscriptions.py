from datetime import date, timedelta

import pandas as pd
from sqlalchemy import text

import database


def add_user_telegram_subscription(user_id: int, telegram_id: int) -> None:
    query = text(
        'INSERT INTO user_telegram_subscription(user_id, telegram_id) '
        'VALUES (:user_id, :telegram_id)'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(user_id=user_id, telegram_id=telegram_id))
        conn.commit()


def delete_user_telegram_subscription(user_id: int, telegram_id: int) -> None:
    query = text(
        'DELETE FROM user_telegram_subscription '
        'WHERE user_id=:user_id AND telegram_id=:telegram_id'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(user_id=user_id, telegram_id=telegram_id))
        conn.commit()


def delete_all_user_telegram_subscriptions(user_id: int) -> None:
    query = text(
        'DELETE FROM user_telegram_subscription '
        'WHERE user_id=:user_id'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(user_id=user_id))
        conn.commit()


def get_user_tg_subscriptions_df(user_id: int) -> pd.DataFrame:
    """
    Возвращает список подписок пользователя на тг каналы

    return: DataFrame[id, name]
    """
    query = text(
        'SELECT tg.id, tg.name as name '
        'FROM telegram_channel tg '
        'JOIN user_telegram_subscription utg ON tg.id=utg.telegram_id '
        'WHERE utg.user_id=:user_id '
        'ORDER BY tg.name ASC'
    )

    with database.engine.connect() as conn:  # FIXME можно ручками сформировать запрос и сразу в pandas отправить
        data = conn.execute(query.bindparams(user_id=user_id)).all()
        data_df = pd.DataFrame(data, columns=['id', 'name'])

    return data_df


def get_telegram_channel_info(telegram_id: int) -> dict:
    """
    return: dict(id, name, link, industry_id, industry_name)
    """
    query = text(
        'SELECT tg.id, tg.name, tg.link, tg.industry_id, i.name '
        'FROM telegram_channel tg '
        'JOIN industry i ON tg.industry_id=i.id '
        'WHERE tg.id=:telegram_id'
    )

    with database.engine.connect() as conn:  # FIXME можно ручками сформировать запрос и сразу в pandas отправить
        data = conn.execute(query.bindparams(telegram_id=telegram_id)).fetchone()
        data = {
            'id': data[0],
            'name': data[1],
            'link': data[2],
            'industry_id': data[3],
            'industry_name': data[4],
        }

    return data


def get_industry_tg_channels_df(industry_id: int, user_id: int) -> pd.DataFrame:
    """
    Возвращает набор тг каналов по отрасли industry_id
    Если пользователь подписан на тг канал, то is_subscribed=True
    return: DataFrame[id, name, is_subscribed]
    """
    query = text(
        'SELECT tg.id, tg.name, (CASE WHEN utg.user_id IS NULL THEN false ELSE true END) as is_subscribed '
        'FROM telegram_channel tg '
        'LEFT JOIN user_telegram_subscription utg ON tg.id=utg.telegram_id '
        'WHERE industry_id=:industry_id AND (utg.user_id=:user_id OR utg.user_id IS NULL)'
        'ORDER BY tg.name'
    )

    with database.engine.connect() as conn:  # FIXME можно ручками сформировать запрос и сразу в pandas отправить
        data = conn.execute(query.bindparams(industry_id=industry_id, user_id=user_id)).all()
        data_df = pd.DataFrame(data, columns=['id', 'name', 'is_subscribed'])

    return data_df


