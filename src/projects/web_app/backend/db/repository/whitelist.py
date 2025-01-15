from typing import Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Whitelist
from db.repository.base import GenericRepository
from db.pagination import Pagination


class WhitelistRepository(GenericRepository[Whitelist]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Whitelist)

    async def get_list_with_count(
            self,
            email: str | None,
            pagination: Pagination
    ) -> tuple[Sequence[Whitelist], int]:
        """
        Получает список E-Mail ограниченного размера.

        :Union[str, None] email: Опциональный фильтр по E-Mail
        :Pagination pagination: Параметры ограничения выборки
        """
        stmt = sa.select(
            Whitelist,
            sa.func.count().over().label("total")
        )
        if email:
            stmt = stmt.where(sa.func.lower(Whitelist.user_email).like(f"%{email.lower()}%"))
        stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        result = await self._session.execute(stmt)
        rows = result.all()
        if not rows:
            return [], 0
        return [row.Whitelist for row in rows], rows[0].total
