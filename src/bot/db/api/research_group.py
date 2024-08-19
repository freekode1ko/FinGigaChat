"""
CRUD для взаимодействия с таблицей models.ResearchGroup.

Позволяет выполнять стандартные операции
"""
import pandas as pd
import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ResearchGroupCRUD(BaseCRUD[models.ResearchGroup]):
    """Класс, который создает объекты для взаимодействия с таблицей models.ResearchGroup"""

    async def get_all(self) -> pd.DataFrame:
        """
        Возвращает список групп CIB Research

        :returns: DataFrame[id, name]
        """
        async with self._async_session_maker() as session:
            data = await session.execute(sa.select(*self.fields).order_by(self._order))
            return pd.DataFrame(data.all(), columns=self.columns)


research_group_db = ResearchGroupCRUD(models.ResearchGroup, models.ResearchGroup.display_order, logger)
