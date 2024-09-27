import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from db import models


async def get_quote_day_day_param(quote: models.Quotes, session: AsyncSession) -> float | None:
    stmt = await session.execute(
        sa.select(models.QuotesValues)
        .filter_by(quote_id=quote.id)
        .order_by(models.QuotesValues.date.desc())
        .offset(0)
        .limit(2)
    )
    quote_data = stmt.scalars().fetchall()
    if not quote_data:
        return 0
    return (quote_data[1].value - quote_data[0].value) / quote_data[0].value * 100


async def get_quote_last(quote: models.Quotes, session: AsyncSession) -> float | None:
    stmt = await session.execute(
        sa.select(models.QuotesValues)
        .filter_by(quote_id=quote.id)
        .order_by(models.QuotesValues.date.desc())
        .offset(0)
        .limit(1)
    )
    quote_data = stmt.scalars().first()
    if not quote_data:
        print(quote.name)
        return 0
    return quote_data.value
