"""Вспомогательные декораторы"""
import functools
from typing import Callable

from aiogram.types import Message, CallbackQuery

from db.user import is_allow_feature
from log.bot_logger import logger, user_logger


def singleton(cls):
    """Сингелтон"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def check_rights(feature: str):
    """
    Проверка доступа пользователя к текущей функциональности.

    :param feature: Название функциональности, к которой относится декорируемая функция.
    :return:        Обработчик, если пользователю доступна функциональность, либо сообщение о недоступности.
    """
    def func_wrapper(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            if not args or not isinstance(args[0], (Message, CallbackQuery)):
                logger.critical(f'Нет базового tg-объекта в функции {func.__name__}. args: {args}, kwargs: {kwargs}')
                return await func(*args, **kwargs)

            tg_obj = args[0]
            session = kwargs.get('session') if kwargs else None
            is_allow = await is_allow_feature(session, tg_obj.from_user.id, feature)

            if is_allow:
                return await func(*args, **kwargs)

            user_msg = tg_obj.text if isinstance(tg_obj, Message) else tg_obj.data
            user_logger.warning(
                f'*{tg_obj.from_user.id}* {tg_obj.from_user.full_name} - {user_msg}:'
                f' недостаточно прав. Функция - {func.__name__}()'
            )
            return await tg_obj.answer('У Вас недостаточно прав для использования данной команды.')

        return wrapper
    return func_wrapper
