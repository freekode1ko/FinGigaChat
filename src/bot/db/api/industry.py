"""
Модуль для взаимодействия с таблицей отраслей.

Предоставляет стандартный интерфейс взаимодействия с таблицей.
Дает возможность поиска по имени
"""
from typing import Optional, Type

import pandas as pd
from sqlalchemy import func, select

from constants import enums
from db import database
from db.api.subject_interface import SubjectInterface
from db.models import Base, Industry, IndustryAlternative, IndustryDocuments


async def get_by_name(name: str) -> Optional[Industry]:
    """Поиск отрасли по имени."""
    async with database.async_session() as session:
        stmt = select(Industry).where(func.lower(Industry.name) == name.lower())
        result = await session.execute(stmt)
        return result.scalar()


async def get_industry_analytic_files(
        industry_id: Optional[int] = None,
        industry_type: Optional[enums.IndustryTypes] = None,
) -> list[IndustryDocuments]:
    """
    Получить файл аналитики по отрасли

    :param industry_id: айди отрасли
    :param  industry_type: тип отрасли
    :return: список документов
    """
    if industry_id is None and industry_type is None:
        return []

    async with database.async_session() as session:
        stmt = select(IndustryDocuments)

        if industry_id is not None:
            stmt = stmt.where(
                IndustryDocuments.industry_id == industry_id,
            )
        if industry_type is not None:
            stmt = stmt.where(
                IndustryDocuments.industry_type == industry_type.value,
            )
        result = await session.execute(stmt)
        return list(result.scalars())


class IndustryInterface(SubjectInterface):
    """Интейрфейс взаимодействия с отраслями"""

    def __init__(self) -> None:
        super().__init__(
            Industry,
            IndustryAlternative,
            Industry.industry_alternative,
        )

    async def get_industries_from_table(self, table: Type[Base]) -> pd.DataFrame:
        """
        Получить отрасли, которые присутствуют в таблице table.

        :param table: таблицы, где ищем отрасли
        :return: отрасли [id, name, display_order]
        """
        async with database.async_session() as session:
            subquery = select(table.industry_id.distinct()).subquery()
            stmt = select(
                *self.fields
            ).where(self.table.id.in_(subquery))
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=self.columns)


industry_db = IndustryInterface()
