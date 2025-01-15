from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ProductDocument
from db.repository.base import GenericRepository


class ProductDocumentRepository(GenericRepository[ProductDocument]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ProductDocument)
