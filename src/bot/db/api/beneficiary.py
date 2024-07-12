"""Запросы к бд связанные с бенефициарами."""
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db.database import async_session
from db.models import Beneficiary


async def get_beneficiary_name(ben_id: int) -> str:
    """
    Получение имени бенефициара.

    :param ben_id:   ID бенефициара.
    :return:         Имя бенефициара.
    """
    async with async_session() as session:
        result = await session.execute(select(Beneficiary.name).where(Beneficiary.id == ben_id))
        return result.scalar()


async def get_beneficiary_by_id(ben_id: int) -> Beneficiary:
    """
    Получение бенефициара.

    :param ben_id:   ID бенефициара.
    :return:         Сущность бенефициара.
    """
    async with async_session() as session:
        stmt = (
            select(Beneficiary)
            .options(joinedload(Beneficiary.clients))
            .where(Beneficiary.id == ben_id)
        )
        result = await session.execute(stmt)
        return result.scalar()
