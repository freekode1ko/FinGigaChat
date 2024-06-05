"""Запросы к бд связанные с группой продуктов"""
from typing import Optional

from sqlalchemy import select

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ProductGroupCRUD(BaseCRUD[models.ProductGroup]):
    """Класс, который создает объекты для взаимодействия с таблицей models.ProductGroup"""

    async def get_by_latin_name(self, latin_name: str) -> Optional[models.ProductGroup]:
        """
        Позволяет получить группу продуктов по ее имени на латинице

        :param latin_name: имя группы на латинице
        :returns: Возвращает либо сам объект, который есть в БД, либо None
        """
        async with self._async_session_maker() as session:
            stmt = select(self._table).where(self._table.name_latin == latin_name).limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()


product_group_db = ProductGroupCRUD(models.ProductGroup, models.ProductGroup.display_order, logger)
