import pandas as pd
from sqlalchemy import text, select, func

from db import models, database
from db.database import engine


def update_user_email(user_id: int, user_email: str):
    """Обновление почты существующего пользователя"""
    query = text('UPDATE whitelist SET user_email=:user_email WHERE user_id=:user_id')
    with engine.connect() as conn:
        conn.execute(query.bindparams(user_email=user_email.lower(), user_id=user_id))
        conn.commit()


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
    async with database.async_session() as session:
        stmt = select(
            models.Whitelist.user_id,
            models.Whitelist.username,
            func.array_agg(models.UserIndustrySubscriptions.industry_id.distinct()).label('industry_ids'),
            func.array_agg(models.UserClientSubscriptions.client_id.distinct()).label('client_ids'),
            func.array_agg(models.UserCommoditySubscriptions.commodity_id.distinct()).label('commodity_ids'),
        ).join(
            models.UserIndustrySubscriptions
        ).join(
            models.UserClientSubscriptions
        ).join(
            models.UserCommoditySubscriptions
        ).group_by(models.Whitelist.user_id)
        result = await session.execute(stmt)
        return pd.DataFrame(result.all(), columns=['user_id', 'username', 'industry_ids', 'client_ids', 'commodity_ids'])
