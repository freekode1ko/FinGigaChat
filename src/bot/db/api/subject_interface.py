"""
Реализует стандартный интерфейс взаимодействия с субъектами (клиенты, сырье, отрасли).

Позволяет:
- выгружать информацию по одному субъекту,
- по множеству субъектов,
- выгружать альт имена,
- выгружать новости по subject.id
"""
import datetime
from typing import Any, Optional, Type

import pandas as pd
from sqlalchemy import case, ColumnElement, func, select
from sqlalchemy.orm import InstrumentedAttribute

from configs.config import OTHER_NEWS_COUNT, TOP_NEWS_COUNT
from db import database
from db.models import Article, Base


class SubjectInterface:
    """Реализация интерфейса взаимодействия с таблицами, у которых есть альтернативные имена и которые связаны с новостями"""

    def __init__(
            self,
            table: Type[Base],
            table_alternative: Type[Base],
            relation_alternative: InstrumentedAttribute,
            relation_article: Optional[InstrumentedAttribute] = None,
            table_relation_article: Optional[Type[Base]] = None,
    ) -> None:
        """
        Инициализация объекта, предоставляющего интерфейс для взаимодействия с таблицей table.

        :param table:                   Таблица sqlalchemy.orm, в которой основные данные по клиентам/сырью/отраслям.
        :param table_alternative:       Таблица sqlalchemy.orm с альтернативными именами.
        :param relation_alternative:    sqlalchemy.orm.relationship связь с таблицей альтернаивных имен.
        :param table_relation_article:  Таблица sqlalchemy.orm со связью с новостями и скорами.
        :param relation_article:        sqlalchemy.orm.relationship связь с таблицей новостей (необязательна).
        """
        self.table = table
        self.table_alternative = table_alternative
        self.relation_alternative = relation_alternative
        self.relation_article = relation_article
        self.table_relation_article = table_relation_article

        self.columns = [i.name for i in self.table.__table__.columns]
        self.fields = [getattr(self.table, c) for c in self.columns]

    async def get_all(self) -> pd.DataFrame:
        """
        Выгрузка всех subject

        :returns: DataFrame[все столбцы таблицы self.table] со всеми subject
        """
        async with database.async_session() as session:
            stmt = select(
                *self.fields
            )
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=self.columns)

    async def get_by_ids(self, ids: list[int]) -> pd.DataFrame:
        """
        Выгрузка subject, которые есть в списке ids

        :param ids: список айдишников
        :return: DataFrame[все столбцы таблицы self.table] с subject из списка ids
        """
        async with database.async_session() as session:
            stmt = select(*self.fields).filter(self.table.id.in_(ids))
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=self.columns)

    async def get_by_industry_id(self, industry_id: int) -> pd.DataFrame:
        """
        Выгружает все subject, у которых industry_id == :industry_id

        :returns: DataFrame[все столбцы таблицы self.table] со всеми subject
        """
        async with database.async_session() as session:
            stmt = select(
                *self.fields
            ).where(self.table.industry_id == industry_id)
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=self.columns)

    async def get_other_names(self) -> pd.DataFrame:
        """
        Возвращает датафрейм с альтернативными именами для каждого subject

        :returns: DataFrame['id', 'name', 'other_name']  (subject.id, subject.name,subject_alternative.other_name)
        """
        async with database.async_session() as session:
            stmt = select(
                self.table.id,
                self.table.name,
                self.table_alternative.other_name,
            ).outerjoin(self.relation_alternative)
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=['id', 'name', 'other_name'])

    async def get(self, _id: int) -> dict[str, Any]:
        """
        Возвращает словарь с данными по subject с id==_id

        :returns: dict[все столбцы таблицы self.table]
        """
        async with database.async_session() as session:
            stmt = select(self.table).where(self.table.id == _id)
            result = await session.execute(stmt)
            data = result.scalar()
            return {c: getattr(data, c) for c in self.columns}

    async def get_by_name(self, name: str) -> dict[str, Any]:
        """
        Возвращает словарь с данными по subject с id==_id

        :returns: dict[все столбцы таблицы self.table]
        """
        async with database.async_session() as session:
            stmt = select(self.table).where(func.lower(self.table.name) == name.lower())
            result = await session.execute(stmt)
            data = result.scalar()
            return {c: getattr(data, c) for c in self.columns}

    async def get_articles_by_subject_ids(
            self,
            subject_ids: int | list[int],
            from_date: datetime.datetime = None,
            to_date: datetime.datetime = None,
            order_by: str | ColumnElement = None,
    ) -> list[tuple[Article, int]]:
        """
        Выгрузка новостей по subject_ids

        :param subject_ids: id клиента/сырьевого товара
        :param from_date: Ограничение снизу по дате
        :param to_date: Ограничение сверху по дате в запросе
        :param order_by: Параметр сортировки в запросе
        :returns: list[tuple[Article, int]]
        """
        if not isinstance(subject_ids, list):
            subject_ids = [subject_ids]

        async with database.async_session() as session:
            stmt = (
                select(Article, self.table.id)
                .join(self.relation_article)
                .join(self.table)
                .where(self.table.id.in_(subject_ids))
                .order_by(self.table.id)
            )

            if from_date is not None:
                stmt = stmt.where(Article.date >= from_date)
            if to_date is not None:
                stmt = stmt.where(Article.date <= to_date)
            if order_by is not None:
                stmt = stmt.order_by(order_by)

            result = await session.execute(stmt)
            return list(result.all())

    @staticmethod
    def _get_new_score_col(score_col: ColumnElement) -> case:
        """
        Формирование колонки с новыми баллами значимости новости (для сортировки новостей).

        :param score_col:   Колонка с баллом значимости новости.
        :return:            Колонку с новым расчетом балла значимости.
        """
        # Расчет new_score по формуле = score - разница между текущ. датой и датой публикации новости (в днях)
        diff = datetime.datetime.now() - Article.date
        days_diff = func.extract('epoch', diff) / (60 * 60 * 24)
        new_score = score_col - days_diff
        # Если при расчете new_score < 0, то присваиваем ему 1
        new_score = case((new_score <= 0, 1), else_=new_score)
        return new_score

    async def get_sort_articles_by_id(
            self,
            subject_id: int,
            limit_val: Optional[int] = None,
            offset_val: int = 0
    ) -> list[tuple[str, datetime.datetime, str, str]]:
        """
        Получение актуальных и отсортированных новостей по объекту.

        :param subject_id:  ID объекта.
        :param limit_val:   Количество нужных новостей.
        :param offset_val:  Сколько сначала нужно пропустить новостей.
        :return:            Список с атрибутами новостей [title, date, link, text_sum].
        """
        subject_id_col, _, score_col = self.table_relation_article.__table__.columns
        new_score = self._get_new_score_col(score_col)

        base_stmt = (
            select(Article.title, Article.date, Article.link, Article.text_sum)
            .join(self.relation_article)
            .where(subject_id_col == subject_id)
            .where(score_col > 0)
        )

        async with database.async_session() as session:
            # Получение топ самых свежих новостей
            stmt_top_3 = base_stmt.order_by(Article.date.desc()).limit(TOP_NEWS_COUNT)
            top_result = await session.execute(stmt_top_3)
            top_articles = top_result.all()
            links_of_top = [article[2] for article in top_articles]
            if offset_val:
                top_articles = []  # Для очистки в send_next_news топ новостей

            # Получение оставшихся новостей
            limit_val = limit_val if limit_val else OTHER_NEWS_COUNT
            stmt_other = (
                base_stmt
                .where(Article.link.notin_(links_of_top))
                .order_by(new_score.desc(), Article.date.desc())
                .offset(offset_val)
                .limit(limit_val)
            )
            other_result = await session.execute(stmt_other)
            other_articles = other_result.all()

            return top_articles + other_articles
