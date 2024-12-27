import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Product
from db.repository.base import GenericRepository


class ProductRepository(GenericRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def get_by_pk_with_documents(self, pk: int) -> Product | None:
        """Возвращает продукт с документами по ID"""
        result = await self._session.execute(
            sa.select(Product)
            .options(selectinload(Product.documents))
            .where(Product.id == pk)
        )
        return result.scalars().first()

    async def get_products_tree(self) -> list[Product]:
        """
        Получает все продукты со списком дочерних продуктов.
        Возвращает корневые продукты (parent_id = 0).
        """
        stmt = sa.select(Product).options(
            selectinload(Product.documents),
            selectinload(Product.children),
        )
        result = await self._session.execute(stmt)
        return [product for product in result.scalars() if product.parent_id == 0]
