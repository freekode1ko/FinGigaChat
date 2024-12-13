from typing import Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import RegisteredUser
from db.repository.base import GenericRepository
from db.pagination import Pagination


class UserRepository(GenericRepository[RegisteredUser]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RegisteredUser)

    async def get_list_with_count(
            self,
            email: str | None,
            role_id: int | None,
            pagination: Pagination
    ) -> tuple[Sequence[RegisteredUser], int]:
        """
        Получает список E-Mail ограниченного размера.

        :Union[str, None] email: Опциональный фильтр по E-Mail
        :Pagination pagination: Параметры ограничения выборки
        """
        stmt = sa.select(
            RegisteredUser,
            sa.func.count().over().label("total")
        )
        if email:
            stmt = stmt.where(sa.func.lower(RegisteredUser.user_email).like(f"%{email.lower()}%"))
        if role_id:
            stmt = stmt.where(RegisteredUser.role_id == role_id)
        stmt = stmt.offset(pagination.offset).limit(pagination.limit)
        result = await self._session.execute(stmt)
        rows = result.all()
        if not rows:
            return [], 0
        return [row.RegisteredUser for row in rows], rows[0].total

    async def is_new_user_email(self, email: str) -> bool:
        """
        Проверяет, занята указанная почта или нет.

        :param str email: Почта пользователя
        :return: True, если пользователя с такой почтой нет, иначе False
        """
        query = sa.select(RegisteredUser.user_email).where(sa.func.lower(RegisteredUser.user_email) == email.lower())
        result = await self._session.execute(query)
        return not result.scalar()

    async def get_user_id_by_email(self, email: str) -> int:
        """
        Получение идентификатора пользователя по его email.

        :param str email: Почта пользователя
        :return: Идентификатор пользователя
        """
        query = sa.select(RegisteredUser.user_id).where(RegisteredUser.user_email == email)
        id_ = await self._session.execute(query)
        return int(id_.scalar())
