import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from db import models


async def get_quote_day_day_param(quote: models.Quotes, session: AsyncSession) -> float | None:
    stmt = await session.execute(
        sa.select(models.QuotesValues)
        .filter_by(quote_id=quote.id)
        .order_by(models.QuotesValues.date.desc())
        .limit(2)
    )
    quote_data = stmt.scalars().fetchall()
    if not quote_data or len(quote_data) < 2:  # мб вернуть 'N/A' или null
        return 0
    return (quote_data[0].value - quote_data[1].value) / quote_data[1].value * 100


async def get_quote_last(quote: models.Quotes, session: AsyncSession) -> float | None:
    stmt = await session.execute(
        sa.select(models.QuotesValues)
        .filter_by(quote_id=quote.id)
        .order_by(models.QuotesValues.date.desc())
        .limit(1)
    )
    quote_data = stmt.scalars().first()
    if not quote_data:
        return 0
    return quote_data.value
