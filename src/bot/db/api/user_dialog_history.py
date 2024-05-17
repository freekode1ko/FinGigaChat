import sqlalchemy as sa

from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger

DIALOG = 'dialog'
EMPTY_DIALOG: dict[str, list] = {DIALOG: []}


class UserDialogHistoryCRUD(BaseCRUD[models.UserDialogHistory]):
    """Класс, который создает объекты для взаимодействия с таблицей models.UserDialogHistory."""

    async def get_user_dialog(self, user_id: int, is_knowledge: bool) -> dict[str, list[dict]]:
        """
        Получение истории диалога между пользователем и Базой Знаний или между пользователем и GiGaChat.

        :param user_id:         Telegram id пользователя.
        :param is_knowledge:    Флаг работы с памятью между пользователем и Базой Знаний (False -> GigaChat).
        :return:                История диалога.
        """
        user_dialog_obj = await self.get(user_id)
        if user_dialog_obj is None:
            user_dialog_obj = models.UserDialogHistory(
                user_id=user_id,
                knowledge_dialog=EMPTY_DIALOG,
                giga_dialog=EMPTY_DIALOG
            )
            await self.create(user_dialog_obj)
            return EMPTY_DIALOG

        if is_knowledge:
            return user_dialog_obj.knowledge_dialog
        return user_dialog_obj.giga_dialog

    async def update_dialog(self, user_id: int, dialog: dict[str, list], is_knowledge: bool) -> None:
        """
        Обновление истории диалога.

        :param user_id:         Telegram id пользователя.
        :param dialog:          История диалога.
        :param is_knowledge:    Флаг работы с памятью между пользователем и Базой Знаний (False -> GigaChat).
        """
        col = self._table.knowledge_dialog if is_knowledge else self._table.giga_dialog
        async with self._async_session_maker() as session:
            stmt = sa.update(self._table).values({col.name: dialog}).where(self._table.user_id == user_id)
            await session.execute(stmt)
            await session.commit()

    async def add_msgs_to_user_dialog(self, user_id: int, messages: dict[str, str], is_knowledge: bool) -> None:
        """
        Добавление сообщений в историю диалога между пользователем и Базой Знаний или между пользователем и GiGaChat.

        :param user_id:         Telegram id пользователя.
        :param is_knowledge:    Тип памяти, по умолчанию история диалога между пользователем и Базой Знаний.
        :param messages:        Диалог из двух сообщений: пользователь и База Знаний (GiGaChat).
        """
        dialog = await self.get_user_dialog(user_id, is_knowledge)
        dialog[DIALOG].append(messages)
        await self.update_dialog(user_id, dialog, is_knowledge)

    async def clear_user_dialog(self, user_id: int, is_knowledge: bool) -> None:
        """
        Очистка истории диалога между пользователем и Базой Знаний или между пользователем и GiGaChat.

        :param user_id:         Telegram id пользователя.
        :param is_knowledge:    Флаг работы с памятью между пользователем и Базой Знаний (False -> GigaChat).
        """
        await self.update_dialog(user_id, EMPTY_DIALOG, is_knowledge)


user_dialog_history_db = UserDialogHistoryCRUD(models.UserDialogHistory, models.UserDialogHistory.user_id, logger)
