"""Запросы к бд связанные с пользовательскими подписками"""
import pandas as pd
import sqlalchemy as sa

from db import database
from db.api.subscriptions_interface import SubscriptionInterface
from db.models import TelegramChannel, TelegramGroup, TelegramSection, UserTelegramSubscriptions


class TelegramSubscriptionInterface(SubscriptionInterface):
    """Интерфейс для взаимодействия с подписками telegram каналов"""

    def __init__(self) -> None:
        """Инициализация объекта, предоставляющего интерфейс для взаимодействия с подписками на telegram каналы"""
        super().__init__(UserTelegramSubscriptions, 'telegram_id', TelegramChannel)
        self.group_table = TelegramGroup
        self.section_table = TelegramSection

    async def delete_all_by_group_id(self, user_id: int, group_id: int) -> None:
        """
        Удаляет все подписки пользователя на элементы из subject_table

        :param user_id: registered_user.user_id
        :param group_id: bot_telegram_group.id
        """
        async with database.async_session() as session:
            subquery = sa.select(
                self.subject_table.id
            ).where(
                self.subject_table.section_id.in_(
                    sa.select(self.section_table.id).where(self.section_table.group_id == group_id)
                )
            ).subquery()

            await session.execute(
                sa.delete(self.table)
                .where(
                    self.table.user_id == user_id,
                    getattr(self.table, self.subject_id_field).in_(subquery)
                )
            )
            await session.commit()

    async def get_subscription_df_by_group_id(self, user_id: int, group_id: int) -> pd.DataFrame:
        """
        Возвращает список подписок пользователя на элементы из subject_table

        :param user_id: registered_user.user_id
        :param group_id: bot_telegram_group.id
        :returns: DataFrame[id, name]
        """
        async with database.async_session() as session:
            subquery = sa.select(self.section_table.id).where(self.section_table.group_id == group_id).subquery()

            result = await session.execute(
                sa.select(
                    self.subject_table.id,
                    self.subject_table.name,
                ).join(
                    self.table, getattr(self.table, self.subject_id_field) == self.subject_table.id
                ).where(
                    self.table.user_id == user_id,
                    self.subject_table.section_id.in_(subquery),
                ).order_by(self.subject_table.name)
            )
            data = result.all()
            return pd.DataFrame(data, columns=['id', 'name'])

    async def get_subject_df_by_group_id(self, user_id: int, group_id: int) -> pd.DataFrame:
        """
        Список элементов с флагом is_subscribed

        :param user_id: registered_user.user_id
        :param group_id: bot_telegram_group.id
        :returns: DataFrame[id, name, is_subscribed]
        """
        async with database.async_session() as session:
            subquery = sa.select(self.section_table.id).where(self.section_table.group_id == group_id).subquery()

            result = await session.execute(
                sa.select(
                    self.subject_table.id,
                    self.subject_table.name,
                    sa.case(
                        (self.table.user_id.is_(None), False),
                        else_=True,
                    ).label('is_subscribed'),
                ).outerjoin(
                    self.table,
                    (
                        (getattr(self.table, self.subject_id_field) == self.subject_table.id) &
                        (self.table.user_id == user_id)
                    ),
                ).where(
                    self.subject_table.section_id.in_(subquery),
                ).order_by(self.subject_table.name)
            )
            data = result.all()
            return pd.DataFrame(data, columns=['id', 'name', 'is_subscribed'])

    async def get_subject_df_by_section_id(self, user_id: int, section_id: int) -> pd.DataFrame:
        """
        Список элементов с флагом is_subscribed

        :param user_id: registered_user.user_id
        :param section_id: bot_telegram_section.id
        :returns: DataFrame[id, name, is_subscribed]
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
                ).outerjoin(
                    self.table,
                    (
                        (getattr(self.table, self.subject_id_field) == self.subject_table.id) &
                        (self.table.user_id == user_id)
                    )
                ).where(
                    self.subject_table.section_id == section_id,
                ).order_by(self.subject_table.name)
            )
            data = result.all()
            return pd.DataFrame(data, columns=['id', 'name', 'is_subscribed'])


user_telegram_subscription_db = TelegramSubscriptionInterface()
