"""Запросы к бд связанные с бенефициарами."""
from sqlalchemy import select

from db.database import async_session
from db.models import Beneficiary, Client, RelationClientBeneficiary


async def get_beneficiary_clients(ben_id: int) -> list[Client]:
    """
    Получение клиентов, относящихся к бенефициару.

    :param ben_id:   ID бенефициара.
    :return:         Список из клиентов, относящихся к бенефициару.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Client)
            .join(RelationClientBeneficiary)
            .where(RelationClientBeneficiary.beneficiary_id == ben_id)
        )
        return result.scalars().all()


async def get_beneficiary_name(ben_id: int) -> str:
    """
    Получение имени бенефициара.

    :param ben_id:   ID бенефициара.
    :return:         Имя бенефициара.
    """
    async with async_session() as session:
        result = await session.execute(select(Beneficiary.name).where(Beneficiary.id == ben_id))
        return result.scalar()
