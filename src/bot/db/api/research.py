"""CRUD для взаимодействия с таблицей models.Research.

Позволяет выполнять стандартные операции,
выгружать новые отчеты,
выгружать отчеты за период,
выгружать отчеты по типу отчета
"""
import datetime
from typing import Optional

import pandas as pd
import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from db.models import ResearchResearchType
from log.bot_logger import logger


class ResearchCRUD(BaseCRUD[models.Research]):
    """Класс, который создает объекты для взаимодействия с таблицей models.Research"""

    async def get_new_researches(self) -> pd.DataFrame:
        """
        Вынимает новые отчеты из таблицы research

        :returns: DataFrame[id, research_type_id, filepath, header, text, parse_datetime, publication_date, report_id]
        """
        async with self._async_session_maker() as session:
            stmt = (
                sa.select(self._table, ResearchResearchType)
                .join(ResearchResearchType, self._table.id == ResearchResearchType.research_id)
                .where(self._table.is_new == True)  # noqa:E712
            )
            data = await session.execute(stmt)

            stmt = sa.update(self._table).values(is_new=False).where(self._table.is_new == True)  # noqa:E712
            await session.execute(stmt)
            await session.commit()

            data_df = pd.DataFrame(data.all(), columns=(*self.columns, 'research_type_id'))

        return data_df

    async def get_researches_over_period(
            self,
            from_date: datetime.date,
            to_date: datetime.date,
            research_type_ids: Optional[list[int]] = None,
    ) -> pd.DataFrame:
        """
        Возвращает все отчеты по отрасли [клиенту] за период с from_date по to_date

        Если research_type_ids не пустой массив, то отчеты вынимаются только где research_type_id=ANY(research_type_ids)

        :param from_date: от какой даты_времени вынимаются
        :param to_date: до какой даты_времени вынимаются
        :param research_type_ids: ID типов отчетов, по которым выгружаются отчеты (по умолчанию все отчеты)
        :returns: DataFrame[id, research_type_id, filepath, header, text, parse_datetime, publication_date, report_id]
        """
        stmt = (
            sa.select(*self.fields, ResearchResearchType.research_type_id)
            .select_from(self._table)
            .join(ResearchResearchType, self._table.id == ResearchResearchType.research_id)
            .where(self._table.publication_date >= from_date, self._table.publication_date <= to_date)
            .order_by(self._table.publication_date)
        )

        if research_type_ids:
            stmt = stmt.where(ResearchResearchType.research_type_id.in_(research_type_ids))

        async with self._async_session_maker() as session:
            data = await session.execute(stmt)
            data_df = pd.DataFrame(data.all(), columns=(*self.columns, 'research_type_id'))

        return data_df

    async def get_researches_by_type(self, research_type_id: int) -> pd.DataFrame:
        """
        Вынимает отчеты из таблицы research

        :param research_type_id: id типа отчета, который вынимается (по умолчанию все)
        :returns: DataFrame[id, research_type_id, filepath, header, text, parse_datetime, publication_date, report_id]
        """
        async with self._async_session_maker() as session:
            stmt = (
                sa.select(*self.fields, ResearchResearchType.research_type_id)
                .join(ResearchResearchType, self._table.id == ResearchResearchType.research_id)
                .where(ResearchResearchType.research_type_id == research_type_id)
            )

            data = await session.execute(stmt)
            data_df = pd.DataFrame(data.all(), columns=(*self.columns, 'research_type_id'))

        return data_df


research_db = ResearchCRUD(models.Research, models.Research.publication_date.desc(), logger)
