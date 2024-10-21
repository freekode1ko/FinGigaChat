"""Функциия для работы с БД"""
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as insert_pg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import ColumnCollectionConstraint, Index

from db import models

ConstraintType = Union[str, ColumnCollectionConstraint, Index, None]


async def custom_insert_or_update_to_postgres(
        session: AsyncSession,
        model: DeclarativeBase,
        values: dict | list[dict],
        constraint: ConstraintType,
) -> None:
    """Вставка или обновление в постгрес"""
    if not values:
        return
    if not isinstance(values, list):
        values = [values]

    for value in values:
        insert_stmt = insert_pg(model).values(value)
        upsert_stmt = insert_stmt.on_conflict_do_update(
            constraint=constraint,
            set_={c.key: c for c in insert_stmt.excluded}
        )
        await session.execute(upsert_stmt)
    await session.commit()


async def get_or_load_quote_section_by_name(session: AsyncSession, name: str, params: dict[str, str] | None) -> models.QuotesSections:
    """Получить QuotesSection по имени или создать ее"""
    if not params:
        params = {}

    stmt = await session.execute(
        sa.select(models.QuotesSections).filter_by(name=name))
    section = stmt.scalar_one_or_none()

    if section is None:
        section = models.QuotesSections(
            name=name,
            params=params,
        )
        session.add(
            section
        )
        await session.flush()
        await session.commit()
    return section
