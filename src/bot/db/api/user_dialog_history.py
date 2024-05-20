import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger

DIALOG = 'dialog'
EMPTY_DIALOG: dict[str, list] = {DIALOG: []}


class UserDialogHistoryCRUD(BaseCRUD[models.UserDialogHistory]):
    """Класс, который создает объекты для взаимодействия с таблицей models.UserDialogHistory."""

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

    async def update_dialog(self, user_id: int, dialog: dict[str, list]) -> None:
        """
        Обновление истории диалога.

        :param user_id:         Telegram id пользователя.
        :param dialog:          История диалога.
        """
        async with self._async_session_maker() as session:
            stmt = sa.update(self._table).values(dialog=dialog).where(self._table.user_id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def add_msgs_to_user_dialog(self, user_id: int, messages: dict[str, str]) -> None:
        """
        Добавление сообщений в историю диалога между пользователем и ИИ.

        :param user_id:         Telegram id пользователя.
        :param messages:        Диалог из двух сообщений: пользователь и ИИ.
        """
        dialog = await self.get_user_dialog(user_id)
        dialog[DIALOG].append(messages)
        await self.update_dialog(user_id, dialog)

    async def clear_user_dialog(self, user_id: int) -> None:
        """
        Очистка истории диалога между пользователем и ИИ.

        :param user_id:         Telegram id пользователя.
        """
        await self.update_dialog(user_id, EMPTY_DIALOG)


user_dialog_history_db = UserDialogHistoryCRUD(models.UserDialogHistory, models.UserDialogHistory.user_id, logger)
