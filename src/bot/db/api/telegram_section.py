import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class TelegramSectionCRUD(BaseCRUD[models.TelegramSection]):
    """Класс, который создает объекты для взаимодействия с таблицей models.TelegramSection"""

    async def get_by_group_id(self, group_id: int) -> list[models.TelegramSection]:
        async with self._async_session_maker() as session:
            stmt = sa.select(self._table).where(self._table.group_id == group_id).order_by(self._order)
            result = await session.scalars(stmt)
            return list(result)


telegram_section_db = TelegramSectionCRUD(models.TelegramSection, models.TelegramSection.display_order, logger)
