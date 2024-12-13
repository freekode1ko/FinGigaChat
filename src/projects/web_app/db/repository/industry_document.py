from sqlalchemy.ext.asyncio import AsyncSession

from db.models import IndustryDocuments
from db.repository.base import GenericRepository


class IndustryDocumentRepository(GenericRepository[IndustryDocuments]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, IndustryDocuments)
