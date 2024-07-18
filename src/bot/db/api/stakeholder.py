"""Запросы к бд связанные со стейкхолдерами."""
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Stakeholder, RelationClientStakeholder


async def get_stakeholder_by_id(session: AsyncSession, sh_id: int) -> Stakeholder:
    """
    Получение стейкхолдера.

    :param session:  Сессия для взаимодействия с бд.
    :param sh_id:    ID стейкхолдера.
    :return:         Сущность стейкхолдера.
    """
    stmt = (
        select(Stakeholder)
        .options(joinedload(Stakeholder.clients))
        .where(Stakeholder.id == sh_id)
    )
    return await session.scalar(stmt)


async def get_stakeholder_types(session: AsyncSession, sh_id: int) -> Sequence[str]:
    """
     Получение уникальных значений в колонке stakeholder_type для стейкхолдеров.

     :param session:  Сессия для взаимодействия с бд.
     :param sh_id:    ID стейкхолдера.
     :return:         Сущность стейкхолдера.
     """
    stmt = (
        select(RelationClientStakeholder.stakeholder_type)
        .distinct()
        .where(RelationClientStakeholder.stakeholder_id == sh_id)
        .order_by(RelationClientStakeholder.stakeholder_type.desc())
    )
    ben_type = await session.scalars(stmt)
    return ben_type.all()
