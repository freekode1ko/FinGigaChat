"""Мидлвейр для отчистки состояния, если прошло времени больше, чем STATE_TIMEOUT или пользователь ввел команду."""
import asyncio
import datetime as dt
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from configs.config import BACKGROUND_TASK_TIMEOUT, BASE_DATETIME_FORMAT, STATE_TIMEOUT
from db.redis import user_constants
from log.bot_logger import logger


async def cancel_task(task_name: str):
    """Отмена задачи по ее имени"""
    for t in asyncio.all_tasks():
        if t.get_name() == task_name:
            logger.warning(f'Отмена задачи {task_name} из-за слишком долгого выполнения')
            t.cancel()
            try:
                await t
            except asyncio.CancelledError:
                logger.info(f'Задача {task_name} успешно отменена')


class StateMiddleware(BaseMiddleware):
    """Класс, реализующий выход из состояния при определенных условиях."""

    @staticmethod
    def get_user_id(event: types.Update) -> int | None:
        """
        Получить пользовательский id.

        :param event:   Объект Telegram, содержащий информацию о пользователе и его действиях в боте.
        :return:        ID пользователя или None в случае неуспешного получения ID.
        """
        user = getattr(event.message, 'from_user', None) or getattr(event.callback_query, 'from_user', None)
        if user:
            return user.id
        logger.error(f'Не удалось получить id пользователя в StateMiddleware, event: {event}')
        return None

    @staticmethod
    async def get_last_activity_date(user_id: int) -> dt.datetime | None:
        """Получение времени последнего сообщения от бота в диалоге с пользователем."""
        last_activity_date = await user_constants.get_user_constant(user_constants.ACTIVITY_NAME, user_id)
        return dt.datetime.strptime(last_activity_date, BASE_DATETIME_FORMAT) if last_activity_date else None

    @staticmethod
    async def update_raw_state_if_timeout(
            last_activity: dt.datetime,
            raw_state: State | None,
            state: FSMContext
    ) -> State | None:
        """
        Обновить состояния в None, если после последнего сообщения бота прошло > STATE_TIMEOUT.

        :param last_activity:   Дата последней активности бота.
        :param raw_state:       Значение состояния.
        :param state:           Объект состояния.
        :return:                None или входное значение состояния.
        """
        if last_activity and raw_state:
            diff = dt.datetime.utcnow() - last_activity
            if diff > STATE_TIMEOUT:
                await state.clear()
                return None
        return raw_state

    @staticmethod
    async def delete_background_task_if_timeout(last_activity: dt.datetime, user_id: int) -> bool:
        """
        Обновить состояния в None, если после последнего сообщения бота прошло > STATE_TIMEOUT.

        :param last_activity:   Дата последней активности бота.
        :param user_id:         ID пользователя.
        :return:                Удалена ли фоновая задача (True - удалена).
        """
        if last_activity:
            diff = dt.datetime.utcnow() - last_activity
            if diff > BACKGROUND_TASK_TIMEOUT:
                await cancel_task(f'{user_constants.BACKGROUND_TASK_NAME}{user_id}')
                await user_constants.del_user_constant(user_constants.BACKGROUND_TASK_NAME, user_id)
                return True
        return False

    async def __call__(
            self,
            handler: Callable[[types.Update, dict[str, Any]], Awaitable[Any]],
            event: types.Update,
            data: dict[str, Any]
    ) -> Any:
        """
        Сбрасывать состояние, если после последнего сообщения бота прошло > STATE_TIMEOUT или пользователь написал команду.

        :param handler: Обработчик.
        :param event:   Событие.
        :param data:    Контекстные данные.
        """
        user_id = self.get_user_id(event)
        last_activity = await self.get_last_activity_date(user_id)
        raw_state = data.get('raw_state')
        state = data.get('state')

        background_task = await user_constants.get_user_constant(user_constants.BACKGROUND_TASK_NAME, user_id)
        if background_task:
            if not await self.delete_background_task_if_timeout(last_activity, user_id):
                waiting_msg = '⏳ Повторите свой запрос после того, как я закончу отвечать на предыдущий'
                if event.message:
                    await event.message.reply(waiting_msg)
                else:
                    await event.bot.send_message(user_id, waiting_msg)
                return

        try:
            if event.message.text.startswith('/') and raw_state:
                data['raw_state'] = None
                await state.clear()
                return await handler(event, data)
        except AttributeError:
            pass

        if user_id is None:
            return await handler(event, data)

        data['raw_state'] = await self.update_raw_state_if_timeout(last_activity, raw_state, state)
        await handler(event, data)
        activity_date = dt.datetime.utcnow().strftime(BASE_DATETIME_FORMAT)
        await user_constants.update_user_constant(user_constants.ACTIVITY_NAME, user_id, activity_date)
