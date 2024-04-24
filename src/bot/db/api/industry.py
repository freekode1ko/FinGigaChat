from datetime import datetime, timedelta
from typing import Any, Optional

import pandas as pd
from sqlalchemy import text, select

from constants import enums
from db import database
from db.api.subject_interface import SubjectInterface
from db.models import Industry, IndustryAlternative, IndustryDocuments


def get_industries_with_tg_channels() -> pd.DataFrame:
    query = 'SELECT id, name FROM industry WHERE id IN (SELECT industry_id FROM telegram_channel) ORDER BY name;'
    industry_df = pd.read_sql(query, con=database.engine)
    return industry_df


def get_industry_name(industry_id: int) -> str:
    with database.engine.connect() as conn:
        query = text('SELECT name FROM industry WHERE id=:industry_id')
        industry_name = conn.execute(query.bindparams(industry_id=industry_id)).scalar_one()

    return industry_name


def get_industry_tg_news(
        industry_id: int, by_user_subscriptions: bool, user_id: int, tmdelta: timedelta, to_datetime: datetime = None
) -> pd.DataFrame:
    """
    Возвращает все тг-новости по отрасли за {days} дней с текущего числа
    Если my_subscriptions == True, то новости вынимаются только из каналов, на которые подписан пользователь

    :param industry_id: ID отрасли, по которой формируется сводка
    :param by_user_subscriptions: Флаг указания, что сводка по подпискам или по всем тг каналам отрасли
    :param user_id: telegram ID пользователя, для которого формируется сводка
    :param tmdelta: Промежуток, за который формируется сводка новостей до to_datetime
    :param to_datetime: до какой даты_времени вынимаются новости (по умолчанию datetime.datetime.now())
    return: DataFrame['telegram_channel_name', 'telegram_article_link', 'title', 'date']
    """
    query = (
        'SELECT tg.name as telegram_channel_name, a.link as telegram_article_link, a.title, a.date '
        'FROM article a '
        'JOIN relation_telegram_article ra ON a.id=ra.article_id '
        'JOIN telegram_channel tg ON ra.telegram_id=tg.id '
        'WHERE tg.industry_id=:industry_id AND '
        'a.date BETWEEN :from_datetime AND :to_datetime '
        '{dop_condition} '
        'ORDER BY tg.name ASC, a.date DESC, ra.telegram_score DESC'
    )
    to_datetime = to_datetime or datetime.now()
    from_datetime = to_datetime - tmdelta
    kwargs = {
        'to_datetime': to_datetime,
        'from_datetime': from_datetime,
        'industry_id': industry_id,
    }

    if not by_user_subscriptions:
        dop_condition = ''
    else:
        dop_condition = 'AND tg.id IN (SELECT telegram_id FROM user_telegram_subscription WHERE user_id=:user_id)'
        kwargs['user_id'] = user_id

    query = text(query.format(dop_condition=dop_condition)).bindparams(**kwargs)

    with database.engine.connect() as conn:  # FIXME можно ручками сформировать запрос и сразу в pandas отправить
        data = conn.execute(query).all()
        data_df = pd.DataFrame(data, columns=['telegram_channel_name', 'telegram_article_link', 'title', 'date'])

    return data_df


async def get_by_name(name: str) -> dict[str, Any]:
    async with database.async_session() as session:
        stmt = select(Industry).where(Industry.name == name)
        result = await session.execute(stmt)
        data = result.fetchone()
        data = {
            'id': data[0],
            'name': data[1],
        }
        return data


async def get_industry_analytic_files(
        industry_id: Optional[int] = None,
        industry_type: Optional[enums.IndustryTypes] = None,
) -> list[IndustryDocuments]:
    if industry_id is None and industry_type is None:
        return []

    async with database.async_session() as session:
        stmt = select(IndustryDocuments).where(
            IndustryDocuments.industry_id == industry_id,
            IndustryDocuments.industry_type == industry_type.value,
        )
        result = await session.execute(stmt)
        return result.all()


industry_db = SubjectInterface(Industry, IndustryAlternative, Industry.industry_alternative)
