from typing import Any, Optional

import pandas as pd
from sqlalchemy import text, select

from constants import enums
from db import database
from db.api.subject_interface import SubjectInterface
from db.models import Industry, IndustryAlternative, IndustryDocuments


def get_industries_with_tg_channels() -> pd.DataFrame:
    query = 'SELECT id, name FROM industry WHERE id IN (SELECT industry_id FROM telegram_channel) ORDER BY name;'
    industry_df = pd.read_sql(query, con=database.engine)
    return industry_df


def get_industry_name(industry_id: int) -> str:
    with database.engine.connect() as conn:
        query = text('SELECT name FROM industry WHERE id=:industry_id')
        industry_name = conn.execute(query.bindparams(industry_id=industry_id)).scalar_one()

    return industry_name


async def get_by_name(name: str) -> dict[str, Any]:
    async with database.async_session() as session:
        stmt = select(Industry).where(Industry.name == name)
        result = await session.execute(stmt)
        data = result.fetchone()
        data = {
            'id': data[0],
            'name': data[1],
        }
        return data


async def get_industry_analytic_files(
        industry_id: Optional[int] = None,
        industry_type: Optional[enums.IndustryTypes] = None,
) -> list[IndustryDocuments]:
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
