"""Запросы к бд связанные с курсами валют"""
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ExcCRUD(BaseCRUD[models.Exc]):
    """Класс, который создает объекты для взаимодействия с таблицей models.Exc"""

    def __init__(self) -> None:
        """Инициализировать интерфейс ExcCRUD"""
        super().__init__(models.Exc, models.Exc.display_order, logger)

    def _get(self) -> sa.Select:
        """
        Получить запрос для выгрузки курсов валют с подгрузкой тип курсов валют, связанного источника данных

        :returns: Возвращает запрос для выгрузки курсов валют
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

    async def get_all(self) -> list[models.Exc]:
        """
        Получить все курсы валют

        :returns: Список курсов
        """
        async with self._async_session_maker() as session:
            result = await session.scalars(self._get())
            return list(result)


exc_db = ExcCRUD()
