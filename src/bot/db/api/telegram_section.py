"""
Модуль с CRUD для таблицы bot_telegram_section
"""
import datetime

import pandas as pd
import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class TelegramSectionCRUD(BaseCRUD[models.TelegramSection]):
    """Класс, который создает объекты для взаимодействия с таблицей models.TelegramSection"""

    async def get_all(self, only_with_channels: bool = True) -> list[models.TelegramSection]:
        """
        Получение списка всех телеграм разделов

        :param only_with_channels: Флаг, что выдавать только те разделы, в которых есть тг каналы
        :returns: Список телеграм разделов
        """
        async with self._async_session_maker() as session:
            stmt = sa.select(self._table).order_by(self._order)

            if only_with_channels:
                subquery = sa.select(models.TelegramChannel.section_id).subquery()
                stmt = stmt.where(self._table.id.in_(subquery))

            result = await session.scalars(stmt)
            return list(result)

    async def get_by_group_id(self, group_id: int, only_with_channels: bool = True) -> list[models.TelegramSection]:
        """
        Получение списка телеграм разделов по group_id

        :param group_id: id группы, к которой принадлежат выгружаемые разделы
        :param only_with_channels: Флаг, что выдавать только те разделы, в которых есть тг каналы
        :returns: Список телеграм разделов
        """
        async with self._async_session_maker() as session:
            stmt = sa.select(self._table).where(self._table.group_id == group_id).order_by(self._order)

            if only_with_channels:
                subquery = sa.select(models.TelegramChannel.section_id).subquery()
                stmt = stmt.where(self._table.id.in_(subquery))

            result = await session.scalars(stmt)
            return list(result)

    async def get_section_tg_news(
            self,
            section_id: int,
            by_user_subscriptions: bool,
            user_id: int,
            tmdelta: datetime.timedelta,
            to_datetime: datetime.datetime = None,
    ) -> pd.DataFrame:
        """
        Возвращает все тг-новости по разделу за {days} дней с текущего числа
        Если my_subscriptions == True, то новости вынимаются только из каналов, на которые подписан пользователь

        :param section_id: ID раздела, по которой формируется сводка
        :param by_user_subscriptions: Флаг указания, что сводка по подпискам или по всем тг каналам отрасли
        :param user_id: telegram ID пользователя, для которого формируется сводка
        :param tmdelta: Промежуток, за который формируется сводка новостей до to_datetime
        :param to_datetime: до какой даты_времени вынимаются новости (по умолчанию datetime.datetime.now())
        return: DataFrame['telegram_channel_name', 'telegram_article_link', 'title', 'date']
        """
        to_datetime = to_datetime or datetime.datetime.now()
        from_datetime = to_datetime - tmdelta

        stmt = sa.select(
            models.TelegramChannel.name,
            models.Article.link,
            models.Article.title,
            models.Article.date,
        ).select_from(
            models.Article
        ).join(
            models.RelationTelegramArticle, models.RelationTelegramArticle.article_id == models.Article.id
        ).join(
            models.TelegramChannel, models.RelationTelegramArticle.telegram_id == models.TelegramChannel.id
        ).where(
            models.TelegramChannel.section_id == section_id,
            models.Article.date > from_datetime,
            to_datetime >= models.Article.date,
        )
        if by_user_subscriptions:
            subquery = sa.select(
                models.UserTelegramSubscriptions.telegram_id
            ).where(
                models.UserTelegramSubscriptions.user_id == user_id
            )
            stmt = stmt.where(models.TelegramChannel.id.in_(subquery))

        async with self._async_session_maker() as session:
            data = await session.execute(stmt)
            data = data.all()
            data_df = pd.DataFrame(data, columns=['telegram_channel_name', 'telegram_article_link', 'title', 'date'])

        return data_df


telegram_section_db = TelegramSectionCRUD(models.TelegramSection, models.TelegramSection.display_order, logger)
