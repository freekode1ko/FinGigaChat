import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Product
from db.repository.base import GenericRepository


class ProductRepository(GenericRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def get_products_tree(self) -> list[Product]:
        stmt = sa.select(Product).options(
            selectinload(Product.documents),
            selectinload(Product.children),
        )
        result = await self._session.execute(stmt)
        products = result.scalars().all()
        return [product for product in products if product.parent_id == 0]
