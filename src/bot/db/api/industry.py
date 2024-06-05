"""
Модуль для взаимодействия с таблицей отраслей.

Предоставляет стандартный интерфейс взаимодействия с таблицей.
Дает возможность поиска по имени
"""
from typing import Optional

from sqlalchemy import func, select

from constants import enums
from db import database
from db.api.subject_interface import SubjectInterface
from db.models import Industry, IndustryAlternative, IndustryDocuments


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


industry_db = SubjectInterface(Industry, IndustryAlternative, Industry.industry_alternative)
