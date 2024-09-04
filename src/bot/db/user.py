"""Запросы к бд связанные с models.user"""
import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as insert_pg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from db import database, models
from db.database import engine


def is_new_user_email(user_email: str) -> bool:
    """Проверка на наличие почты в таблице (занята кем-то или нет)"""
    query = select(models.RegisteredUser.user_email).where(func.lower(models.RegisteredUser.user_email) == user_email.lower())
    with engine.connect() as conn:
        return not conn.execute(query).scalar()


def is_user_email_exist(user_id: int) -> str | None:
    """Проверка наличия почты у пользователя"""
    query = select(models.RegisteredUser.user_email).where(models.RegisteredUser.user_id == user_id)
    with engine.connect() as conn:
        return conn.execute(query).scalar()


async def get_users_subscriptions() -> pd.DataFrame:
    """
    Получить подписки пользователя

    :return: подписки
    """
    async with database.async_session() as session:
        stmt = select(
            models.RegisteredUser.user_id,
            models.RegisteredUser.username,
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
        ).group_by(models.RegisteredUser.user_id)
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
        ins = insert_pg(models.RegisteredUser).values(
            user_id=user_id,
            username=user_username,
            full_name=user_full_name,
            user_type='user',
            user_status='active',
            user_email=user_email,
            role_id=await get_base_user_role_id(session),
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
                'role_id': ins.excluded.role_id,
            }
        )
        await session.execute(ins)
        await session.commit()


async def get_user(session: AsyncSession, user_id: int) -> models.RegisteredUser | None:
    """
    Получить ORM объект пользователя по телеграм user_id.

    :param session: Асинхронная сессия базы данных.
    :param user_id: user.user_id
    :return:        ORM объект пользователя
    """
    return await session.get(models.RegisteredUser, user_id)


async def get_user_role(session: AsyncSession, user: models.RegisteredUser) -> models.UserRole:
    """
    Получение роли пользователя.

    :param session:    Сессия бд.
    :param user:       Сущность пользователя.
    :return:           Объект UserRole, соответсвующий id.
    """
    stmt = (
        select(models.UserRole)
        .options(joinedload(models.UserRole.features))
        .where(models.UserRole.id == user.role_id)
    )
    result = await session.execute(stmt)
    role = result.unique().scalar()
    return role


async def get_base_user_role_id(session: AsyncSession) -> int:
    """
    Получение id бозовой роли: user.

    :param session: Сессия бд.
    :return:        Id роли user.
    """
    return await session.scalar(
        select(models.UserRole.id)
        .where(models.UserRole.name == 'user')
    )
