"""Запросы к бд связанные с models.whitelist"""
import pandas as pd
from sqlalchemy import func, select, text
from sqlalchemy.dialects.postgresql import insert as insert_pg
from sqlalchemy.ext.asyncio import AsyncSession

from db import database, models
from db.database import engine


def is_new_user_email(user_email: str) -> bool:
    """Проверка на наличие почты в таблице (занята кем-то или нет)"""
    query = text('SELECT user_email FROM whitelist WHERE LOWER(user_email)=:user_email')
    with engine.connect() as conn:
        return not conn.execute(query.bindparams(user_email=user_email.lower())).scalar()


def is_user_email_exist(user_id: int) -> bool:
    """Проверка наличия почты у пользователя"""
    query = select(models.Whitelist.user_email).where(models.Whitelist.user_id == user_id)
    with engine.connect() as conn:
        return conn.execute(query).all()


async def get_users_subscriptions() -> pd.DataFrame:
    """
    Получить подписки пользователя

    :return: подписки
    """
    async with database.async_session() as session:
        stmt = select(
            models.Whitelist.user_id,
            models.Whitelist.username,
            func.coalesce(
                func.array_agg(
                    models.UserIndustrySubscriptions.industry_id.distinct()
                ).filter(models.UserIndustrySubscriptions.industry_id != None),  # noqa:E711
                [],
            ).label('industry_ids'),
            func.coalesce(
                func.array_agg(
                    models.UserClientSubscriptions.client_id.distinct()
                ).filter(models.UserClientSubscriptions.client_id != None),  # noqa:E711
                [],
            ).label('client_ids'),
            func.coalesce(
                func.array_agg(
                    models.UserCommoditySubscriptions.commodity_id.distinct()
                ).filter(models.UserCommoditySubscriptions.commodity_id != None),  # noqa:E711
                [],
            ).label('commodity_ids'),
        ).outerjoin(
            models.UserIndustrySubscriptions
        ).outerjoin(
            models.UserClientSubscriptions
        ).outerjoin(
            models.UserCommoditySubscriptions
        ).group_by(models.Whitelist.user_id)
        result = await session.execute(stmt)
        return pd.DataFrame(result.all(),
                            columns=['user_id', 'username', 'industry_ids', 'client_ids', 'commodity_ids'])


async def insert_user_email_after_register(
        user_id: int,
        user_username: str,
        user_full_name: str,
        user_email: str) -> None:
    """
    Сохранение почты после регистрации

    :param user_id: ID пользователя
    :param user_username: Username пользователя
    :param user_full_name: Имя пользователя
    :param user_email: Email пользователя
    """
    async with database.async_session() as session:
        ins = insert_pg(models.Whitelist).values(
            user_id=user_id,
            username=user_username,
            full_name=user_full_name,
            user_type='user',
            user_status='active',
            user_email=user_email,
        )
        ins = ins.on_conflict_do_update(
            constraint='whitelist_pkey',
            set_={
                'user_id': ins.excluded.user_id,
                'username': ins.excluded.username,
                'full_name': ins.excluded.full_name,
                'user_type': 'user',
                'user_status': 'active',
                'user_email': ins.excluded.user_email,
            }
        )
        await session.execute(ins)
        await session.commit()


async def get_user(session: AsyncSession, user_id: int) -> models.Whitelist | None:
    """
    Получить ORM объект пользователя по телеграм user_id.

    :param session: Асинхронная сессия базы данных.
    :param user_id: whitelist.user_id
    :return:        ORM объект пользователя
    """
    item = await session.get(models.Whitelist, user_id)
    return item


async def get_users(session: AsyncSession) -> list[models.Whitelist]:
    """
    Получить пользователей.

    :param session: Асинхронная сессия базы данных.
    :return:        Список пользователей
    """
    items = await session.scalars(select(models.Whitelist))
    return list(items)
