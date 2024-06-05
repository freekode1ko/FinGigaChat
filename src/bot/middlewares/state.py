"""Мидлвейр для отчистки состояния, если прошло времени больше, чем STATE_TIMEOUT или пользователь ввел команду."""
import datetime as dt
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.state import State
from aiogram.types import TelegramObject

from configs.config import BASE_DATETIME_FORMAT, STATE_TIMEOUT
from db.redis.last_activity import get_last_activity, update_last_activity
from log.bot_logger import logger


class StateMiddleware(BaseMiddleware):
    """Класс, реализующий выход из состояния при определенных условиях."""

    @staticmethod
    def get_user_id(event: TelegramObject) -> int:
        """
        Получение пользовательского id.

        :param event:   Объект Telegram, содержащий информацию о пользователе и его действиях в боте.
        :return:        ID пользователя или 0 в случае ошибки.
        """
        if event.message is not None:
            user_id = event.message.from_user.id
        else:
            try:
                user_id = event.callback_query.from_user.id
            except Exception as e:
                logger.error(f'{type(e)}: не удалось получить id пользователя в ActivityMiddleware: {e}')
                user_id = 0
        return user_id

    @staticmethod
    async def set_raw_state(user_id: int, raw_state: State | None) -> State | None:
        """
        Обновление состояния в None, если после последнего сообщения бота прошло > STATE_TIMEOUT.

        :param user_id:     ID пользователя.
        :param raw_state:   Значение состояния.
        :return:            None или входное значение состояния.
        """
        last_activity_date = await get_last_activity(user_id)

        if last_activity_date and raw_state:
            last_activity_date = dt.datetime.strptime(last_activity_date, BASE_DATETIME_FORMAT)
            diff = dt.datetime.utcnow() - last_activity_date
            if diff.seconds > STATE_TIMEOUT:
                return None
        return raw_state

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ):
        """
        Сбрасывает состояние, в котором находится пользователь, если после последнего сообщения бота прошло > STATE_TIMEOUT.
        Или пользователь написал команду.

        :param handler: Обработчик.
        :param event:   Событие.
        :param data:    Контекстные данные.
        """
        raw_state = data.get('raw_state')

        if event.message and event.message.text.startswith('/') and raw_state:
            data['raw_state'] = None
            await handler(event, data)
            return

        user_id = self.get_user_id(event)
        if not user_id:
            await handler(event, data)
            return

        data['raw_state'] = await self.set_raw_state(user_id, raw_state)
        await handler(event, data)
        activity_data = dt.datetime.utcnow().strftime(BASE_DATETIME_FORMAT)
        await update_last_activity(user_id, activity_data)
