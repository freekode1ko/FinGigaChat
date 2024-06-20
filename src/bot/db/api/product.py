"""Запросы к бд связанные с продуктами"""
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ProductCRUD(BaseCRUD[models.Product]):
    """Класс, который создает объекты для взаимодействия с таблицей models.Product"""

    def __init__(self) -> None:
        """Инициализировать интерфейс ProductCRUD"""
        super().__init__(models.Product, models.Product.display_order, logger)

    def _get(self) -> sa.Select:
        """Получить запрос для выгрузки продукта"""
        stmt = (
            sa.select(self._table)
            .options(
                joinedload(self._table.parent),
                joinedload(self._table.children),
                joinedload(self._table.documents),
            )
        )
        return stmt

    @staticmethod
    def _sort_children(item: models.Product | None) -> models.Product | None:
        """Отсортировать детей"""
        if isinstance(item, models.Product):
            item.children = sorted(item.children, key=lambda x: x.display_order)
            return item

    async def get(self, id_: int) -> models.Product | None:
        """Получить продукт по его ID"""
        async with self._async_session_maker() as session:
            result = await session.execute(self._get().where(self._table.id == id_).limit(1))
            return self._sort_children(result.unique().scalar_one_or_none())

    async def get_by_latin_name(self, latin_name: str) -> models.Product | None:
        """
        Получить продукт по его имени на латинице

        :param latin_name: имя на латинице
        :returns: Возвращает либо сам объект, который есть в БД, либо None
        """
        async with self._async_session_maker() as session:
            stmt = self._get().where(self._table.name_latin == latin_name).limit(1)
            result = await session.execute(stmt)
            return self._sort_children(result.unique().scalar_one_or_none())

    async def get_root(self) -> models.Product | None:
        """
        Получить корневой продукт

        :returns: Возвращает либо сам объект, который есть в БД, либо None
        """
        async with self._async_session_maker() as session:
            stmt = self._get().filter_by(parent_id=None).limit(1)
            result = await session.execute(stmt)
            return self._sort_children(result.unique().scalar_one_or_none())


product_db = ProductCRUD()
