from typing import Sequence

import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Commodity, CommodityResearch
from db.repository.base import GenericRepository


class CommodityRepository(GenericRepository[Commodity]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Commodity)

    async def get_by_id_with_researches(self, commodity_id: int) -> Commodity | None:
        """Получает Commodity со списком исследований"""
        query = (
            sa.select(Commodity)
            .where(Commodity.id == commodity_id)
            .options(joinedload(Commodity.commodity_research))
        )
        result = await self._session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_with_researches(self) -> Sequence[Commodity]:
        """Получает список Commodity со списком исследований"""
        query = (
            sa.select(Commodity)
            .options(joinedload(Commodity.commodity_research))
            .order_by(Commodity.id)
        )
        result = await self._session.execute(query)
        return result.unique().scalars().all()

    async def add_commodity_research(self, commodity: Commodity, commodity_research: CommodityResearch) -> None:
        """Добавляет исследование для Commodity"""
        commodity.commodity_research.append(commodity_research)
        await self._session.commit()
