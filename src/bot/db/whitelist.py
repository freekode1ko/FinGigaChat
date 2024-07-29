"""Запросы к бд связанные с models.whitelist"""
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from db import models


async def is_email_in_whitelist(session: AsyncSession, user_email: str) -> bool:
    """
    Проверить, есть ли эл. почта в белом списке?

    :param session:     Асинхронная сессия с БД
    :param user_email:  Эл. почта пользователя
    :return:            True если почта в белом списке, иначе False
    """
    result = await session.execute(sa.select(
        sa.case(
            (sa.func.count(models.Whitelist.user_email) > 0, True),
            else_=False,
        )
    ).where(sa.func.lower(models.Whitelist.user_email) == user_email.lower()))
    return result.scalar()
