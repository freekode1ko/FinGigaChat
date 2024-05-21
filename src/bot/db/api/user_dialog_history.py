"""Методы по взаимодействию с таблицей UserDialogHistory в БД."""
import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger

DIALOG = 'dialog'
EMPTY_DIALOG: dict[str, list] = {DIALOG: []}


class UserDialogHistoryCRUD(BaseCRUD[models.UserDialogHistory]):
    """Класс, который создает объекты для взаимодействия с таблицей models.UserDialogHistory."""

    async def _update_dialog(self, user_id: int, dialog: dict[str, list]) -> None:
        """
        Обновление истории диалога.

        :param user_id:         Telegram id пользователя.
        :param dialog:          История диалога.
        """
        async with self._async_session_maker() as session:
            stmt = sa.update(self._table).values(dialog=dialog).where(self._table.user_id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def get_user_dialog(self, user_id: int) -> dict[str, list[dict]]:
        """
        Получение истории диалога между пользователем и ИИ.

        :param user_id:         Telegram id пользователя.
        :return:                История диалога.
        """
        user_dialog_obj = await self.get(user_id)
        if user_dialog_obj is None:
            user_dialog_obj = models.UserDialogHistory(
                user_id=user_id,
                dialog=EMPTY_DIALOG,
            )
            await self.create(user_dialog_obj)
            return EMPTY_DIALOG
        return user_dialog_obj.dialog

    async def add_msgs_to_user_dialog(self, user_id: int, messages: dict[str, str], need_replace: bool = False) -> None:
        """
        Добавление или изменение сообщений в историю диалога между пользователем и ИИ.

        :param user_id:         Telegram id пользователя.
        :param messages:        Диалог из двух сообщений: пользователь и ИИ.
        :param need_replace:     Необходимость замены последних сообщений новыми.
        """
        dialog = await self.get_user_dialog(user_id)
        if need_replace and len(dialog[DIALOG]):
            dialog[DIALOG].pop()
        dialog[DIALOG].append(messages)
        await self._update_dialog(user_id, dialog)

    async def clear_user_dialog(self, user_id: int) -> None:
        """
        Очистка истории диалога между пользователем и ИИ.

        :param user_id:      Telegram id пользователя.
        """
        await self._update_dialog(user_id, EMPTY_DIALOG)

    async def get_last_user_query(self, user_id: int) -> str:
        """
        Получение последнего пользовательского запроса.

        :param user_id:     Telegram id пользователя.
        :return:            Последний пользовательский запрос.
        """
        user_dialog_obj = await self.get(user_id)
        if user_dialog_obj is None or not len(user_dialog_obj.dialog[DIALOG]):
            return ''
        return user_dialog_obj.dialog[DIALOG][-1]['user']


user_dialog_history_db = UserDialogHistoryCRUD(models.UserDialogHistory, models.UserDialogHistory.user_id, logger)
