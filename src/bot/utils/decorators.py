"""Вспомогательные декораторы"""
import functools
from typing import Callable

from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from utils.base import is_registered_user, is_user_has_access_to_feature
from log.bot_logger import user_logger


def singleton(cls):
    """Сингелтон"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def has_access_to_feature(feature: str, is_need_answer: bool = True):
    """
    Проверка доступа пользователя к полученной функциональности.

    :param feature:         Название функциональности, к которой относится декорируемая функция.
    :param is_need_answer:  Необходимо ли отправить ответ об "отсутствии прав на использование команды".
    :return:                Обработчик, если пользователю доступна функциональность,
                            либо сообщение о недоступности,
                            либо False, если сообщение отправлять не нужно (задекорирована промежуточная функция).
    """
    def func_wrapper(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # намеренно сделано без обработки исключений, чтобы сразу править обработчики при добавлении декоратора
            tg_obj: Message | CallbackQuery = args[0]
            session: AsyncSession = kwargs['session']

            user_id = tg_obj.from_user.id
            full_name = tg_obj.from_user.full_name
            user_msg = tg_obj.text if isinstance(tg_obj, Message) else tg_obj.data

            registered_user = await is_registered_user(session, tg_obj, user_id, full_name, user_msg, func.__name__)
            if not registered_user:
                return

            access = await is_user_has_access_to_feature(session, registered_user, feature)
            if access:
                return await func(*args, **kwargs)

            if not is_need_answer:  # без отправки сообщения, если это промежуточная функция (обработчик в обработчике)
                return False
            user_logger.warning(f'*{user_id}* {full_name} - {user_msg} : недостаточно прав. Функция: {func.__name__}()')
            await tg_obj.answer('У Вас недостаточно прав для использования данной команды.')

        return wrapper
    return func_wrapper
