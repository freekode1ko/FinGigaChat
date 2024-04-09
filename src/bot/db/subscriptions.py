import datetime
from typing import Any, Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db import database


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
        'LEFT JOIN user_telegram_subscription utg ON tg.id=utg.telegram_id and utg.user_id=:user_id '
        'WHERE industry_id=:industry_id AND (utg.user_id=:user_id OR utg.user_id IS NULL)'
        'ORDER BY tg.name'
    )

    with database.engine.connect() as conn:  # FIXME можно ручками сформировать запрос и сразу в pandas отправить
        data = conn.execute(query.bindparams(industry_id=industry_id, user_id=user_id)).all()
        data_df = pd.DataFrame(data, columns=['id', 'name', 'is_subscribed'])

    return data_df


# ------------------ RESEARCH SUBSCRIPTIONS METHODS -----------------------
def get_user_research_subscriptions_df(user_id: int) -> pd.DataFrame:
    """
    Возвращает список подписок пользователя на отчеты CIB Research

    return: DataFrame[id, name]
    """
    query = text(
        'SELECT rt.id, rt.name as name '  # FIXME
        'FROM research_type rt '
        'JOIN user_research_subscription urs ON rt.id=urs.research_type_id '
        'WHERE urs.user_id=:user_id '
        'ORDER BY rt.name ASC'
    )

    with database.engine.connect() as conn:
        data = conn.execute(query.bindparams(user_id=user_id)).all()
        data_df = pd.DataFrame(data, columns=['id', 'name'])

    return data_df


def get_research_type_info(research_type_id: int) -> dict:
    """
    Возвращает информацию по типу отчета CIB Research

    :param research_type_id: research_type.id
    return: dict(id, name, description, research_section_id)
    """
    query = text(
        'SELECT rt.id, rt.name, rt.description, rt.research_section_id, rt.summary_type '
        'FROM research_type rt '
        'WHERE rt.id=:research_type_id'
    )

    with database.engine.connect() as conn:  # FIXME можно ручками сформировать запрос и сразу в pandas отправить
        data = conn.execute(query.bindparams(research_type_id=research_type_id)).fetchone()
        data = {
            'id': data[0],
            'name': data[1],
            'description': data[2],
            'research_section_id': data[3],
            'summary_type': data[4],
        }

    return data


def add_user_research_subscription(user_id: int, research_type_id: int) -> None:
    """
    Подписывает пользователя на отчет CIB Research

    :param user_id: whitelist.user_id
    :param research_type_id: research_type.id
    """
    query = text(
        'INSERT INTO user_research_subscription(user_id, research_type_id) '
        'VALUES (:user_id, :research_type_id)'
    )

    with database.engine.connect() as conn:
        try:
            conn.execute(query.bindparams(user_id=user_id, research_type_id=research_type_id))
            conn.commit()
        except IntegrityError:
            conn.rollback()


def delete_user_research_subscription(user_id: int, research_type_id: int) -> None:
    """
    Отписывает пользователя от отчета CIB Research

    :param user_id: whitelist.user_id
    :param research_type_id: research_type.id
    """
    query = text(
        'DELETE FROM user_research_subscription '
        'WHERE user_id=:user_id AND research_type_id=:research_type_id'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(user_id=user_id, research_type_id=research_type_id))
        conn.commit()


def add_user_cib_section_subscription(user_id: int, research_section_id: int) -> None:
    """
    Подписывает пользователя на все отчеты CIB Research, которые принадлежат разделу research_section_id

    :param user_id: whitelist.user_id
    :param research_section_id: research_section.id
    """
    query = text(
        'INSERT INTO user_research_subscription(user_id, research_type_id) '
        'SELECT :user_id, rt.id FROM research_type rt WHERE research_section_id=:research_section_id'
    )

    with database.engine.connect() as conn:
        try:
            conn.execute(query.bindparams(user_id=user_id, research_section_id=research_section_id))
            conn.commit()
        except IntegrityError:
            conn.rollback()


def delete_user_cib_section_subscription(user_id: int, research_section_id: int) -> None:
    """
    Отписывает пользователя от отчетов CIB Research, которые принадлежат разделу research_section_id

    :param user_id: whitelist.user_id
    :param research_section_id: research_section.id
    """
    query = text(
        'DELETE FROM user_research_subscription '
        'WHERE user_id=:user_id AND '
        '   research_type_id IN (SELECT id FROM research_type WHERE research_section_id=:research_section_id)'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(user_id=user_id, research_section_id=research_section_id))
        conn.commit()


def get_cib_group_info(group_id: int) -> dict[str, Any]:
    """
    Возвращает информацию по группе CIB Research
    return: dict[id, name, ]
    """
    query = text(
        'SELECT rg.id, rg.name '
        'FROM research_group rg '
        'WHERE rg.id=:group_id'
    )

    with database.engine.connect() as conn:
        data = conn.execute(query.bindparams(group_id=group_id)).fetchone()
        data = {
            'id': data[0],
            'name': data[1],
        }
    return data


def get_research_groups_df() -> pd.DataFrame:
    """
    Возвращает список групп CIB Research

    return: DataFrame[id, name]
    """
    query = text(
        'SELECT rg.id, rg.name '
        'FROM research_group rg '
    )

    with database.engine.connect() as conn:
        data = conn.execute(query).all()
        data_df = pd.DataFrame(data, columns=['id', 'name'])

    return data_df


def get_cib_sections_by_group_df(group_id: int, user_id: int) -> pd.DataFrame:
    """
    Возвращает данные по разделам в группе group_id
    Если пользователь подписан на все отчеты в разделе, то у него ставится флаг is_subscribed=True

    :param group_id: research_group.id группы CIB Research
    :param user_id: whitelist.id пользователя
    return: DataFrame[id, name, dropdown_flag, is_subscribed]
    """

    query = text(
        'WITH section_subscriptions AS ('
        '   SELECT count(rt.id) as types_cnt, research_section_id,'
        '        sum(CASE WHEN urg.user_id IS NULL THEN 0 ELSE 1 END) as sub_cnt '
        '   FROM research_type rt '
        '   LEFT JOIN user_research_subscription urg ON rt.id=urg.research_type_id and urg.user_id=:user_id '
        '   WHERE urg.user_id=:user_id OR urg.user_id IS NULL '
        '   GROUP BY research_section_id'
        ')'
        'SELECT rs.id, rs.name, rs.dropdown_flag, '
        '   (CASE WHEN types_cnt = sub_cnt THEN true ELSE false END) as is_subscribed '
        'FROM research_section rs '
        'JOIN section_subscriptions ss ON rs.id=ss.research_section_id '
        'WHERE research_group_id=:group_id '
        'ORDER BY rs.dropdown_flag, rs.name'
    )

    with database.engine.connect() as conn:  # FIXME можно ручками сформировать запрос и сразу в pandas отправить
        data = conn.execute(query.bindparams(group_id=group_id, user_id=user_id)).all()
        data_df = pd.DataFrame(data, columns=['id', 'name', 'dropdown_flag', 'is_subscribed'])

    return data_df


def get_cib_section_info(section_id: int) -> dict[str, Any]:
    """
    Возвращает информацию по разделу CIB Research

    :param section_id: research_section.id
    return: dict(id, name, research_group_id, section_type)
    """
    query = text(
        'SELECT id, name, research_group_id, section_type '
        'FROM research_section '
        'WHERE id=:section_id'
    )

    with database.engine.connect() as conn:
        data = conn.execute(query.bindparams(section_id=section_id)).fetchone()
        data = {
            'id': data[0],
            'name': data[1],
            'research_group_id': data[2],
            'section_type': data[3],
        }

    return data


def get_cib_research_types_by_section_df(section_id: int, user_id: int) -> pd.DataFrame:
    """
    Возвращает набор отчетов по разделу section_id
    Если пользователь подписан на отчет, то is_subscribed=True
    return: DataFrame[id, name, is_subscribed, summary_type]
    """
    query = text(
        'SELECT rt.id, rt.name, (CASE WHEN urg.user_id IS NULL THEN false ELSE true END) as is_subscribed, rt.summary_type '
        'FROM research_type rt '
        'LEFT JOIN user_research_subscription urg ON rt.id=urg.research_type_id and urg.user_id=:user_id '
        'WHERE research_section_id=:section_id AND (urg.user_id=:user_id OR urg.user_id IS NULL)'
        'ORDER BY rt.name'
    )

    with database.engine.connect() as conn:
        data = conn.execute(query.bindparams(section_id=section_id, user_id=user_id)).all()
        data_df = pd.DataFrame(data, columns=['id', 'name', 'is_subscribed', 'summary_type'])

    return data_df


def delete_all_user_research_subscriptions(user_id: int) -> None:
    query = text(
        'DELETE FROM user_research_subscription '
        'WHERE user_id=:user_id'
    )

    with database.engine.connect() as conn:
        conn.execute(query.bindparams(user_id=user_id))
        conn.commit()


def get_new_researches() -> pd.DataFrame:
    """
    Вынимает новые отчеты из таблицы research
    return: DataFrame[id, research_type_id, filepath, header, text, parse_datetime, publication_date, news_id]
    """
    with database.engine.connect() as conn:
        columns = [
            'id',
            'research_type_id',
            'filepath',
            'header',
            'text',
            'parse_datetime',
            'publication_date',
            'news_id',
        ]
        query = text(
            'UPDATE research SET is_new=false '
            'WHERE is_new=true '
            'RETURNING id, research_type_id, filepath, header, text, parse_datetime, publication_date, news_id '
        )
        data = conn.execute(query).all()
        conn.commit()
        data_df = pd.DataFrame(data, columns=columns)

    return data_df


def get_researches_over_period(
        from_date: datetime.date,
        to_date: datetime.date,
        research_type_ids: list[int] = None,
) -> pd.DataFrame:
    """
    Возвращает все отчеты по отрасли [клиенту] за период с from_date по to_date
    Если research_type_ids не пустой массив, то отчеты вынимаются только где research_type_id=ANY(research_type_ids)

    :param from_date: от какой даты_времени вынимаются
    :param to_date: до какой даты_времени вынимаются
    :param research_type_ids: ID типов отчетов, по которым выгружаются отчеты (по умолчанию все отчеты)
    return: DataFrame[id, research_type_id, filepath, header, text, parse_datetime, publication_date, news_id]
    """
    query = (
        'SELECT id, research_type_id, filepath, header, text, parse_datetime, publication_date, news_id '
        'FROM research '
        'WHERE publication_date BETWEEN :from_date AND :to_date '
        '{dop_condition} '
        'ORDER BY publication_date DESC'
    )

    kwargs = {
        'from_date': from_date,
        'to_date': to_date,
    }

    dop_condition = ''
    if research_type_ids:
        dop_condition = 'AND research_type_id=ANY(:research_type_ids)'
        kwargs['research_type_ids'] = research_type_ids

    query = text(query.format(dop_condition=dop_condition)).bindparams(**kwargs)

    with database.engine.connect() as conn:
        columns = [
            'id',
            'research_type_id',
            'filepath',
            'header',
            'text',
            'parse_datetime',
            'publication_date',
            'news_id',
        ]
        data = conn.execute(query).all()
        data_df = pd.DataFrame(data, columns=columns)

    return data_df


def get_researches_by_type(research_type_id: int) -> pd.DataFrame:
    """
    Вынимает отчеты из таблицы research
    :param research_type_id: id типа отчета, который вынимается (по умолчанию все)
    return: DataFrame[id, research_type_id, filepath, header, text, parse_datetime, publication_date, news_id]
    """
    with database.engine.connect() as conn:
        columns = [
            'id',
            'research_type_id',
            'filepath',
            'header',
            'text',
            'parse_datetime',
            'publication_date',
            'news_id',
        ]
        query = text(
            f'SELECT {", ".join(columns)} '
            f'FROM research '
            f'WHERE research_type_id=:research_type_id'
        )
        data = conn.execute(query.bindparams(research_type_id=research_type_id)).all()
        conn.commit()
        data_df = pd.DataFrame(data, columns=columns)

    return data_df


def get_users_by_research_types_df(research_type_ids: list[int]) -> pd.DataFrame:
    """
    return: DataFrame[user_id: int, username: str, research_types: list[int]]
    """
    with database.engine.connect() as conn:
        columns = [
            'user_id',
            'username',
            'research_types',
        ]
        query = text(
            'SELECT u.user_id, u.username, ARRAY_AGG(urs.research_type_id) '
            'FROM user_research_subscription urs '
            'JOIN whitelist u ON u.user_id=urs.user_id '
            'WHERE urs.research_type_id=ANY(:research_type_ids) '
            'GROUP BY u.user_id '
        )
        data = conn.execute(query.bindparams(research_type_ids=research_type_ids)).all()
        data_df = pd.DataFrame(data, columns=columns)

    return data_df


def get_research_sections_by_research_types_df(research_type_ids: list[int]) -> dict[int, dict[str, Any]]:
    """
    return: dict[
        research_type_id: {
            research_section_id: int,
            name: str,
            research_group_id: int,
            research_type_id: int,
        }
    ]
    """
    with database.engine.connect() as conn:
        columns = [
            'research_section_id',
            'name',
            'research_group_id',
            'research_type_id',
        ]
        query = text(
            'SELECT rs.id, rs.name, rs.research_group_id, rt.id '
            'FROM research_type rt '
            'JOIN research_section rs ON rs.id=rt.research_section_id '
            'WHERE rt.id=ANY(:research_type_ids) '
        )
        data = conn.execute(query.bindparams(research_type_ids=research_type_ids)).all()
        data_df = pd.DataFrame(data, columns=columns)
        result = data_df.set_index(data_df['research_type_id']).T.to_dict()

    return result
# ------------------ RESEARCH SUBSCRIPTIONS METHODS END --------------------
