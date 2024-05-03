from typing import Type

import pandas as pd
from sqlalchemy import insert, delete, select, case, or_

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
                insert(self.table),
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
                delete(self.table)
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
                delete(self.table)
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
                select(self.subject_table.id, self.subject_table.name)
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
                select(
                    self.subject_table.id,
                    self.subject_table.name,
                    case(
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
                insert(self.table),
                items[[self.subject_id_field, 'user_id']].to_dict('records')
            )
            await session.commit()

