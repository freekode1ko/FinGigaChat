from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from db.models import Industry, IndustryDocuments
from .base import GenericRepository


class IndustryRepository(GenericRepository[Industry]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Industry)

    async def create_document(self, document: IndustryDocuments) -> None:
        """Создает документ для отрасли"""
        self._session.add(document)
        await self._session.commit()

    async def get_by_pk_with_documents(self, pk: int) -> Industry | None:
        """Возвращает отрасль с документами по ID"""
        result = await self._session.execute(
            sa.select(Industry)
            .options(sa.orm.selectinload(Industry.documents))
            .where(Industry.id == pk)
        )
        return result.scalars().first()

    async def get_list_with_documents(self) -> Sequence[Industry]:
        """Возвращает список отраслей с документами"""
        result = await self._session.execute(
            sa.select(Industry)
            .options(sa.orm.selectinload(Industry.documents))
        )
        return result.scalars().all()
