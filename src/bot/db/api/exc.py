"""Запросы к бд связанные с продуктами"""
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ExcCRUD(BaseCRUD[models.Exc]):
    """Класс, который создает объекты для взаимодействия с таблицей models.Product"""

    def __init__(self) -> None:
        """Инициализировать интерфейс ProductCRUD"""
        super().__init__(models.Exc, models.Exc.display_order, logger)

    def _get(self) -> sa.Select:
        """
        Получить запрос для выгрузки продуктов с подгрузкой подкатегорий, родительской категории, связанных документов

        :returns: Возвращает запрос для выгрузки продуктов
        """
        stmt = (
            sa.select(self._table)
            .order_by(self._order)
            .options(
                joinedload(self._table.exc_type),
                joinedload(self._table.parser_source),
            )
        )
        return stmt

    async def get(self, id_: int) -> models.Exc | None:
        """
        Получить продукт по его ID

        :param id_: ID продукта
        :returns: Возвращает либо сам объект, который есть в БД, либо None
        """
        async with self._async_session_maker() as session:
            result = await session.execute(self._get().where(self._table.id == id_).limit(1))
            return self._sort_children(result.unique().scalar_one_or_none())

    async def get_all(self) -> list[models.Exc]:
        """
        Получить корневой продукт

        :returns: Возвращает либо сам объект, который есть в БД, либо None
        """
        async with self._async_session_maker() as session:
            result = await session.scalars(self._get())
            return list(result)


exc_db = ExcCRUD()
