"""Мидлвейр для отчистки состояния, если прошло времени больше, чем STATE_TIMEOUT или пользователь ввел команду."""
import datetime as dt
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from configs.config import BASE_DATETIME_FORMAT, STATE_TIMEOUT
from db.redis.last_activity import get_last_activity, update_last_activity
from log.bot_logger import logger


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
    async def update_raw_state_if_timeout(user_id: int, raw_state: State | None, state: FSMContext) -> State | None:
        """
        Обновить состояния в None, если после последнего сообщения бота прошло > STATE_TIMEOUT.

        :param user_id:     ID пользователя.
        :param raw_state:   Значение состояния.
        :param state:       Объект состояния.
        :return:            None или входное значение состояния.
        """
        last_activity_date = await get_last_activity(user_id)

        if last_activity_date and raw_state:
            last_activity_date = dt.datetime.strptime(last_activity_date, BASE_DATETIME_FORMAT)
            diff = dt.datetime.utcnow() - last_activity_date
            if diff > STATE_TIMEOUT:
                await state.clear()
                return None
        return raw_state

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
        raw_state = data.get('raw_state')
        state = data.get('state')

        try:
            if event.message.text.startswith('/') and raw_state:
                data['raw_state'] = None
                await state.clear()
                return await handler(event, data)
        except AttributeError:
            pass

        user_id = self.get_user_id(event)
        if user_id is None:
            return await handler(event, data)

        data['raw_state'] = await self.update_raw_state_if_timeout(user_id, raw_state, state)
        await handler(event, data)
        activity_date = dt.datetime.utcnow().strftime(BASE_DATETIME_FORMAT)
        await update_last_activity(user_id, activity_date)
