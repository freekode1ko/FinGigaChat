import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import RegisteredUser
from db.repository.base import GenericRepository


class UserRepository(GenericRepository[RegisteredUser]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RegisteredUser)

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
