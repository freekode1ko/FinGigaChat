"""Вспомогательные декораторы"""
import functools
from typing import Any, Callable

from db.database import async_session
from utils.base import has_access_to_feature_logic


def singleton(cls):
    """Сингелтон"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def has_access_to_feature(feature: str, is_need_answer: bool = True) -> Any:
    """
    Проверка доступа пользователя к полученной функциональности.

    :param feature:         Название функциональности, к которой относится декорируемая функция.
    :param is_need_answer:  Необходимо ли отправить ответ об "отсутствии прав на использование команды".
    :return:                Обработчик, если пользователю доступна функциональность,
                            либо None с сообщением о недоступности,
                            либо False, если сообщение отправлять не нужно (задекорирована промежуточная функция).
    """
    def func_wrapper(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            if session := kwargs.get('session') if kwargs else None:
                return await has_access_to_feature_logic(feature, is_need_answer, func, args, kwargs, session)
            else:
                async with async_session() as ses:
                    return await has_access_to_feature_logic(feature, is_need_answer, func, args, kwargs, ses)

        return wrapper
    return func_wrapper
