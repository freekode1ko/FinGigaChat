"""Модуль с Енумераторами сервиса"""
from __future__ import annotations

from enum import Enum


class Environment(str, Enum):
    """Среда окружения, где запускаем код"""

    STAGE = 'dev'
    PROD = 'prod'
    LOCAL = 'local'
    UNKNOWN = 'unknown'

    def is_local(self) -> bool:
        """Является ли окружение локальным?"""
        return self in (Environment.UNKNOWN, Environment.LOCAL)

    @classmethod
    def from_str(cls, param: str) -> Environment:
        """Получить объект енумератора из переданной строки"""
        try:
            return cls(param.lower())
        except ValueError:
            return cls.UNKNOWN


class RequestType(str, Enum):
    """Тип запроса: на обновление или создание"""

    POST = 'post'
    PUT = 'put'
