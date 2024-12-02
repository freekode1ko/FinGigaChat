import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import SettingsAliases
from db.repository.base import GenericRepository


class SettingsAliasesRepository(GenericRepository[SettingsAliases]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SettingsAliases)

    async def get_by_key(self, key: str) -> SettingsAliases | None:
        """
        Проверяет, существует указанный ключ или нет.

        :param str key: Ключ, по которому осуществляется поиск
        :return: Экземпляр модели SettingsAliases, если ключ существует, иначе None
        """
        query = sa.select(SettingsAliases).where(SettingsAliases.key == key)
        result = await self._session.execute(query)
        return result.scalars().first()
