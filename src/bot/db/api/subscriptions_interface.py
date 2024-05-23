"""
Реализация интерфейса для взаимодействия с подписками на что-либо.

Позволяет:
- подписываться на один субъект,
- отписываться от одного субъекта,
- подписываться на группу субъектов,
- удалять все подписки на субъекты,
- выгружать список подписок,
- выгружать список субъектов с флагом, подписан ли на него пользователь
- подписываться на субъект с именем, которое похоже на имя субъекта другой таблицы
"""
from typing import Type, Iterable

import pandas as pd
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from db import database
from db.models import Base


class SubscriptionInterface:

    def __init__(self, table: Type[Base], subject_id_field: str, subject_table: Type[Base]) -> None:
        """
        Инициализация объекта, предоставляющего интерфейс для взаимодействия с подписками с таблицей table

        :param table: Таблица sqlalchemy.orm с подписками
        :param subject_table: Таблица sqlalchemy.orm, которая содержит элементы, на которые подписывается пользователь
        :param subject_id_field: Название столбца ссылки на элемент subject_table
        """
        self.table = table
        self.subject_table = subject_table
        self.subject_id_field = subject_id_field

    async def add_subscription(self, user_id: int, subject_id: int) -> None:
        """
        Добавляет подписку на элемент из subject_table
        :param user_id: whitelist.user_id
        :param subject_id: subject.id
        """
        async with database.async_session() as session:
            await session.execute(
                sa.insert(self.table),
                [
                    {'user_id': user_id, self.subject_id_field: subject_id}
                ]
            )
            await session.commit()

    async def delete_subscription(self, user_id: int, subject_id: int) -> None:
        """
        Удаляет подписку на элемент из subject_table
        :param user_id: whitelist.user_id
        :param subject_id: subject.id
        """
        async with database.async_session() as session:
            await session.execute(
                sa.delete(self.table)
                .where(
                    getattr(self.table, self.subject_id_field) == subject_id,
                    self.table.user_id == user_id
                )
            )
            await session.commit()

    async def delete_all(self, user_id: int) -> None:
        """
        Удаляет все подписки пользователя на элементы из subject_table
        :param user_id: whitelist.user_id
        """
        async with database.async_session() as session:
            await session.execute(
                sa.delete(self.table)
                .where(
                    self.table.user_id == user_id
                )
            )
            await session.commit()

    async def get_subscription_df(self, user_id: int) -> pd.DataFrame:
        """
        Возвращает список подписок пользователя на элементы из subject_table

        :param user_id: whitelist.user_id
        return: DataFrame[id, name]
        """
        async with database.async_session() as session:
            result = await session.execute(
                sa.select(self.subject_table.id, self.subject_table.name)
                .join(self.table, getattr(self.table, self.subject_id_field) == self.subject_table.id)
                .where(self.table.user_id == user_id)
                .order_by(self.subject_table.name)
            )
            data = result.all()
            return pd.DataFrame(data, columns=['id', 'name'])

    async def get_subject_df(self, user_id: int) -> pd.DataFrame:
        """
        Список элементов с флагом is_subscribed
        :return DataFrame[id, name, is_subscribed]
        """
        async with database.async_session() as session:
            result = await session.execute(
                sa.select(
                    self.subject_table.id,
                    self.subject_table.name,
                    sa.case(
                        (self.table.user_id.is_(None), False),
                        else_=True,
                    ).label('is_subscribed'),
                ).outerjoin(self.table,
                            ((getattr(self.table, self.subject_id_field) == self.subject_table.id) &
                             (self.table.user_id == user_id))
                            )
                .order_by(self.subject_table.name)
            )
            data = result.all()
            return pd.DataFrame(data, columns=['id', 'name', 'is_subscribed'])

    async def add_subscriptions(self, user_id: int, items: pd.DataFrame) -> None:
        """
        Добавление множества подписок

        :param user_id: whitelist.user_id (telegram user_id)
        :param items: DataFrame[id]
        """
        async with database.async_session() as session:
            items['user_id'] = user_id
            items[self.subject_id_field] = items['id']

            if items.empty:
                return

            await session.execute(
                sa.insert(self.table),
                items[[self.subject_id_field, 'user_id']].to_dict('records')
            )
            await session.commit()

    async def subscribe_on_news_source_with_same_name(
        self,
        user_id: int,
        from_table: Type[Base],
        subject_ids: int | list[int],
    ) -> None:
        """
        Подписка на клиента или отрасль, если имя отчета совпадает с именем клиента/отрасли.
        Подписка на отчет, если имя клиента/отрасли совпадает с именем отчета.
        Позволяет делать подписку сразу на группу субъектов

        :param user_id: телеграм id пользователя
        :param from_table: таблица, из которой по subject_ids вынимается поле name для поиска похожих имен в self.subject_table
        :param subject_ids: список id объектов из таблицы from_table
        """
        if not isinstance(subject_ids, Iterable):
            subject_ids = [subject_ids]

        async with database.async_session() as session:
            subquery = sa.select(sa.func.lower(from_table.name)).where(from_table.id.in_(subject_ids)).subquery()

            select_query = sa.select(
                sa.text(f'{user_id}::int'),
                self.subject_table.id,
            ).where(sa.func.lower(self.subject_table.name).in_(subquery)).group_by(self.subject_table.id)
            stmt = insert(
                self.table
            ).from_select(['user_id', self.subject_id_field], select_query).on_conflict_do_nothing()
            await session.execute(stmt)
            await session.commit()

