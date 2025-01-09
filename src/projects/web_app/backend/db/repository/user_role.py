from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserRole
from db.repository.base import GenericRepository


class UserRoleRepository(GenericRepository[UserRole]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserRole)
