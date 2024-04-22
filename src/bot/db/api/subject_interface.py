import datetime
from typing import Any, Type, Optional

import pandas as pd
from sqlalchemy import select, func, ColumnElement
from sqlalchemy.orm import InstrumentedAttribute

from db import database
from db.models import Base, Article


class SubjectInterface:

    def __init__(
            self,
            table: Type[Base],
            table_alternative: Type[Base],
            relation_alternative: InstrumentedAttribute,
            relation_article: Optional[InstrumentedAttribute] = None,
    ) -> None:
        """
        Инициализация объекта, предоставляющего интерфейс для взаимодействия с таблицей table

        :param table: Таблица sqlalchemy.orm, в которой основные данные по клиентам/сырью/отраслям
        :param table_alternative: Таблица sqlalchemy.orm с альтернативными именами
        :param relation_alternative: sqlalchemy.orm.relationship связь с таблицей альтернаивных имен
        :param relation_article: sqlalchemy.orm.relationship связь с таблицей новостей (необязательна)
        """
        self.table = table
        self.table_alternative = table_alternative
        self.relation_alternative = relation_alternative
        self.relation_article = relation_article

        self.columns = [i.name for i in self.table.__table__.columns]
        self.fields = [getattr(self.table, c) for c in self.columns]

    async def get_all(self) -> pd.DataFrame:
        """Выгрузка всех subject"""
        async with database.async_session() as session:
            stmt = select(
                *self.fields
            )
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=self.columns)

    async def get_by_industry_id(self, industry_id: int) -> pd.DataFrame:
        """Выгружает все subject, у которых industry_id == :industry_id"""
        async with database.async_session() as session:
            stmt = select(
                *self.fields
            ).where(self.table.industry_id == industry_id)
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=self.columns)

    async def get_other_names(self) -> pd.DataFrame:
        """Возвращает датафрейм с альтернативными именами для каждого subject"""
        async with database.async_session() as session:
            stmt = select(
                self.table.id,
                self.table.name,
                func.unnest(func.string_to_array(self.table_alternative.other_names, ';')).label('other_name'),
            ).outerjoin(self.relation_alternative)
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=['id', 'name', 'other_name'])

    async def get(self, _id: int) -> dict[str, Any]:
        """Возвращает словарь с данными по subject с id==_id"""
        async with database.async_session() as session:
            stmt = select(self.table).where(self.table.id == _id)
            result = await session.execute(stmt)
            data = result.scalar()
            return {c: getattr(data, c) for c in self.columns}

    async def get_articles_by_subject_id(
            self,
            subject_id: int,
            from_date: datetime.date = None,
            to_date: datetime.date = None,
            order_by: str | ColumnElement = None,
    ) -> list[Article]:
        """
        Выгрузка новостей по subject_id
        :param subject_id: id клиента/сырьевого товара
        :param from_date: Ограничение снизу по дате
        :param to_date: Ограничение сверху по дате в запросе
        :param order_by: Параметр сортировки в запросе
        """
        async with database.async_session() as session:
            stmt = select(Article).join(self.relation_article).join(self.table).where(self.table.id == subject_id)

            if from_date is not None:
                stmt = stmt.where(func.date(Article.date) >= from_date)
            if to_date is not None:
                stmt = stmt.where(func.date(Article.date) <= to_date)
            if order_by is not None:
                stmt = stmt.order_by(order_by)

            result = await session.execute(stmt)
            return list(result.scalars())
