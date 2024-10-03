"""Функциия для работы с БД"""
from typing import Union

from sqlalchemy.dialects.postgresql import insert as insert_pg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import ColumnCollectionConstraint, Index

ConstraintType = Union[str, ColumnCollectionConstraint, Index, None]


async def custom_insert_or_update_to_postgres(
        session: AsyncSession,
        model: DeclarativeBase,
        values: dict,
        constraint: ConstraintType
) -> None:
    """Вставка или обновление в постгрес"""
    insert_stmt = insert_pg(model).values(values)
    upsert_stmt = insert_stmt.on_conflict_do_update(
        constraint=constraint,
        set_={c.key: c for c in insert_stmt.excluded}
    )
    await session.execute(upsert_stmt)
    await session.commit()


async def custom_many_insert_or_update_to_postgres(
        session: AsyncSession,
        model: DeclarativeBase,
        values: list[dict],
        constraint: ConstraintType
) -> None:
    """Вставка или обновление в постгрес список из данных"""
    insert_stmt = insert_pg(model).values(*values)
    upsert_stmt = insert_stmt.on_conflict_do_update(
        constraint=constraint,
        set_={c.key: c for c in insert_stmt.excluded}
    )
    await session.execute(upsert_stmt)
    await session.commit()
