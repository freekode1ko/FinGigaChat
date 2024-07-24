"""
Интерфейс взаимодействия с подписками на отчеты cib Research.

Позволяет выполнять стандартные операции для работы с подписками,
а также позволяет подписываться на все отчеты в разделе
"""
import pandas as pd
import sqlalchemy as sa

from db import database, models
from db.api.subscriptions_interface import SubscriptionInterface


class ResearchSubscriptionInterface(SubscriptionInterface):
    """
    Интерфейс взаимодействия с подписками на отчеты CIB Research.

    Позволяет выполнять стандартные операции для работы с подписками,
    а также позволяет подписываться на все отчеты в разделе
    """

    def __init__(self) -> None:
        """Инициализация объекта, предоставляющего интерфейс для взаимодействия с подписками на cib research"""
        super().__init__(models.UserResearchSubscriptions, 'research_type_id', models.ResearchType)
        self.group_table = models.ResearchGroup
        self.section_table = models.ResearchSection

    async def delete_all_by_section_id(self, user_id: int, section_id: int) -> None:
        """
        Удаляет все подписки пользователя на элементы из subject_table

        :param user_id: user.user_id
        :param section_id: research_section.id
        """
        async with database.async_session() as session:
            subquery = sa.select(self.subject_table.id).where(self.subject_table.research_section_id == section_id).subquery()

            await session.execute(
                sa.delete(self.table).where(
                    self.table.user_id == user_id,
                    getattr(self.table, self.subject_id_field).in_(subquery)
                )
            )
            await session.commit()

    async def get_subject_df_by_section_id(self, user_id: int, section_id: int) -> pd.DataFrame:
        """
        Список элементов с флагом is_subscribed

        :param user_id: user.user_id
        :param section_id: research_section.id
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
                    self.subject_table.summary_type,
                ).select_from(self.subject_table).outerjoin(
                    self.table,
                    (
                        (getattr(self.table, self.subject_id_field) == self.subject_table.id) &
                        (self.table.user_id == user_id)
                    )
                ).where(
                    self.subject_table.research_section_id == section_id
                ).order_by(self.subject_table.name)
            )
            data = result.all()
            return pd.DataFrame(data, columns=['id', 'name', 'is_subscribed', 'summary_type'])

    async def add_subscriptions_by_section_id(self, user_id: int, section_id: int) -> None:
        """
        Добавление подписок на все subject в данном section

        :param user_id: user.user_id
        :param section_id: id раздела research_section
        """
        async with database.async_session() as session:
            select_stmt = sa.select(
                sa.text(f'{user_id}::int'),
                self.subject_table.id
            ).select_from(
                self.subject_table
            ).where(self.subject_table.research_section_id == section_id)

            await session.execute(sa.insert(self.table).from_select(['user_id', 'research_type_id'], select_stmt))
            await session.commit()

    async def get_users_by_research_types_df(self, research_type_ids: list[int]) -> pd.DataFrame:
        """
        Выгрузка пользователей со списком их подписок на отчеты cib research

        :param research_type_ids: список research_type.id, в пределах которого выгружаются подписки на отчеты
        (то есть id вне этого списка не выгружаются)
        :returns: DataFrame[user_id: int, username: str, research_types: list[int]]
        """
        async with database.async_session() as session:
            stmt = sa.select(
                models.User.user_id, models.User.username, models.User.user_email,
                sa.func.array_agg(self.table.research_type_id),
            ).select_from(
                self.table
            ).join(
                models.User, models.User.user_id == self.table.user_id
            ).where(
                self.table.research_type_id.in_(research_type_ids)
            ).group_by(models.User.user_id)

            columns = [
                'user_id',
                'username',
                'user_email',
                'research_types',
            ]
            data = await session.execute(stmt)
            data_df = pd.DataFrame(data.all(), columns=columns)

        return data_df


user_research_subscription_db = ResearchSubscriptionInterface()
