from __future__ import annotations

from enum import Enum


class Environment(str, Enum):
    """
    Среда окружения, где запускаем код
    """

    STAGE = 'dev'
    PROD = 'prod'
    LOCAL = 'local'
    UNKNOWN = 'unknown'

    def is_local(self) -> bool:
        return self in (Environment.UNKNOWN, Environment.LOCAL)

    @classmethod
    def from_str(cls, param: str) -> Environment:
        try:
            return cls(param.lower())
        except ValueError:
            return cls.UNKNOWN


class RetrieverType(Enum):
    """
    Типы ретриверов в боте
    """
    other = 0  # простое обращение к гигачат
    state_support = 1  # ретривер по господдержке
    qa_banker = 2  # ретривер по новостям и финансовым показателям