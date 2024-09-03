"""Вспомогательные декораторы"""
import functools
from typing import Callable

from aiogram.types import Message, CallbackQuery

from db.user import is_allow_feature
from log.bot_logger import logger


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

            if isinstance(args[0], (Message, CallbackQuery)):
                tg_obj = args[0]
                session = kwargs.get('session') if kwargs else None
                is_allow = await is_allow_feature(session, tg_obj.from_user.id, feature)

                if not is_allow:
                    return await tg_obj.answer('Данная функциональность недоступна.')
                return await func(*args, **kwargs)
            logger.critical(f'Нет базового тг объекта в функции {func.__name__}. args: {args}, kwargs: {kwargs}')

        return wrapper
    return func_wrapper
