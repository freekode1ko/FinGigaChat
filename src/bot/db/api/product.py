"""Запросы к бд связанные с продуктами"""
import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ProductCRUD(BaseCRUD[models.Product]):
    """Класс, который создает объекты для взаимодействия с таблицей models.Product"""

    async def get_all_by_group_id(self, group_id: int) -> list[models.Product]:
        """Получить все продукты по айди группы продукта

        :param group_id: айди группы продукта
        :return: список продуктов с данным айди группы
        """
        async with self._async_session_maker() as session:
            stmt = sa.select(self._table).where(self._table.group_id == group_id).order_by(self._order)
            return list(await session.scalars(stmt))


product_db = ProductCRUD(models.Product, models.Product.display_order, logger)
