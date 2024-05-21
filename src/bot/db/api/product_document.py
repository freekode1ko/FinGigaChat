import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ProductDocumentCRUD(BaseCRUD[models.ProductDocument]):
    """Класс, который создает объекты для взаимодействия с таблицей models.Product"""

    async def get_all_by_product_id(self, product_id: int) -> list[models.ProductDocument]:
        async with self._async_session_maker() as session:
            stmt = sa.select(self._table).where(self._table.product_id == product_id).order_by(self._order)
            result = await session.scalars(stmt)
            return list(result)


product_document_db = ProductDocumentCRUD(models.ProductDocument, models.ProductDocument.id, logger)
