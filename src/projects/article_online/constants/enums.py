"""Модуль с Енумераторами сервиса."""
from __future__ import annotations

from enum import Enum


class Environment(str, Enum):
    """Среда окружения, где запускаем код."""

    STAGE = 'dev'
    PROD = 'prod'
    LOCAL = 'local'
    UNKNOWN = 'unknown'

    def is_local(self) -> bool:
        """Является ли окружение локальным?"""
        return self in (Environment.UNKNOWN, Environment.LOCAL)

    @classmethod
    def from_str(cls, param: str) -> Environment:
        """Получить объект енумератора из переданной строки."""
        try:
            return cls(param.lower())
        except ValueError:
            return cls.UNKNOWN


class LinksType(str, Enum):
    """Тип ссылки."""

    subject_link = 'subject_link'  # ссылка на новость, содержащая новость об объекте (клиенте, коммоде и тд)
    tg_link = 'tg_link'  # ссылка на новость из тг-каналов, не относящаяся ни к чему (отрасли)
