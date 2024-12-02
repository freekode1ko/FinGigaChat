"""
CRUD для взаимодействия с таблицей models.ResearchSection.

Позволяет выполнять стандартные операции, выгружать разделы по id группы, выгружать разделы по списку id типов отчетов
"""
from typing import Any

import pandas as pd
import sqlalchemy as sa

from db import database, models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ResearchSectionCRUD(BaseCRUD[models.ResearchSection]):
    """Класс, который создает объекты для взаимодействия с таблицей models.ResearchSection"""

    @staticmethod
    async def get_research_sections_df_by_group_id(group_id: int, user_id: int) -> pd.DataFrame:
        """
        Возвращает данные по разделам в группе group_id

        Если пользователь подписан на все отчеты в разделе, то у него ставится флаг is_subscribed=True

        :param group_id: research_group.id группы CIB Research
        :param user_id: registered_user.id пользователя
        :returns: DataFrame[id, name, dropdown_flag, is_subscribed]
        """
        query = sa.text(
            'WITH section_subscriptions AS ('
            '   SELECT count(rt.id) as types_cnt, research_section_id,'
            '        sum(CASE WHEN urg.user_id IS NULL THEN 0 ELSE 1 END) as sub_cnt '
            '   FROM research_type rt '
            '   LEFT JOIN user_research_subscription urg ON rt.id=urg.research_type_id and urg.user_id=:user_id '
            '   WHERE urg.user_id=:user_id OR urg.user_id IS NULL '
            '   GROUP BY research_section_id'
            ')'
            'SELECT rs.id, rs.name, rs.dropdown_flag, '
            '   (CASE WHEN types_cnt = sub_cnt THEN true ELSE false END) as is_subscribed '
            'FROM research_section rs '
            'JOIN section_subscriptions ss ON rs.id=ss.research_section_id '
            'WHERE research_group_id=:group_id '
            'ORDER BY rs.display_order'
        )

        async with database.async_engine.connect() as conn:
            data = await conn.execute(query.bindparams(group_id=group_id, user_id=user_id))
            data_df = pd.DataFrame(data.all(), columns=['id', 'name', 'dropdown_flag', 'is_subscribed'])

        return data_df

    async def get_research_sections_by_research_types_df(self, research_type_ids: list[int]) -> dict[int, dict[str, Any]]:
        """
        Возвращает словарь, где ключ - это research_type.id, а значение - словарь с данными о разделе, в котором находится данный отчет

        :param research_type_ids: список research_type.id, по которому выгружается информация о том, к какому разделу
         принадлежит данный отчет
        :returns: dict[
            research_type_id: {
                research_section_id: int,
                name: str,
                research_group_id: int,
                research_type_id: int,
            }
        ]
        """
        async with self._async_session_maker() as session:
            stmt = sa.select(
                self._table.id, self._table.name, self._table.research_group_id, models.ResearchType.id
            ).select_from(
                models.ResearchType
            ).join(
                self._table, self._table.id == models.ResearchType.research_section_id
            ).where(models.ResearchType.id.in_(research_type_ids))
            columns = [
                'research_section_id',
                'name',
                'research_group_id',
                'research_type_id',
            ]
            data = await session.execute(stmt)
            data_df = pd.DataFrame(data.all(), columns=columns)
            result = data_df.set_index(data_df['research_type_id']).T.to_dict()

        return result


research_section_db = ResearchSectionCRUD(models.ResearchSection, models.ResearchSection.display_order, logger)
