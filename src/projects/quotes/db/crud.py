"""Функция для работы с БД"""
from typing import Any, Union

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import ColumnCollectionConstraint, Index

from db import models

ConstraintType = Union[str, ColumnCollectionConstraint, Index, None]


async def custom_upsert(
        session: AsyncSession,
        model: DeclarativeBase,
        values: dict | list[dict],
        constraint: str,
        autocommit: bool = True,
) -> None:
    """
    Вставка или обновление в БД, если запись уже существует.

    :param AsyncSession session: Сессия SQLAlchemy
    :param DeclarativeBase model: Модель SQLAlchemy,
    :param dict | list[dict] values: Значения для вставки или обновления
    :param str constraint: Название ограничения
    :param bool autocommit: Коммит изменений В БД в конце выполнения функции
    """
    sqla_constraint = next(
        (c for c in model.__table__.constraints if c.name == constraint),
        None
    )
    if sqla_constraint is None:
        raise ValueError(f'Ограничение {constraint} в {model} не найдено')

    if not values:
        return
    if not isinstance(values, list):
        values = [values]

    for value in values:
        where_stmt = sa.and_(*[
            getattr(model, key) == value[key]
            for key in (col.name for col in sqla_constraint.columns)
        ])
        update_stmt = sa.update(model).where(where_stmt).values(**value)
        result = await session.execute(update_stmt)
        if result.rowcount == 0:
            insert_stmt = sa.insert(model).values(**value)
            await session.execute(insert_stmt)
    if autocommit:
        await session.commit()


async def get_or_load_quote_section_by_name(
        session: AsyncSession,
        name: str,
        params: dict[str, str] | None,
        autocommit: bool = True,
) -> models.QuotesSections:
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
        if autocommit:
            await session.commit()
    return section


async def get_or_load_quote_by_name(
        session: AsyncSession,
        name: str,
        section_id: int,
        insert_content: dict[str, Any] | None = None,
        autocommit: bool = True,
) -> models.Quotes:
    """Получить Quotes по имени или создать ее"""
    if not insert_content:
        insert_content = {}

    stmt = await session.execute(
        sa.select(models.Quotes).filter_by(name=name, quotes_section_id=section_id))
    quote = stmt.scalar_one_or_none()

    if quote is None:
        quote = models.Quotes(
            name=name,
            quotes_section_id=section_id,
            **insert_content,
        )
        session.add(
            quote
        )
        await session.flush()
        if autocommit:
            await session.commit()
    return quote
