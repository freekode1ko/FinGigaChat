from __future__ import annotations

from enum import Enum, IntEnum, auto


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


class ResearchSectionType(Enum):
    """Типы разделов CIB Research, участвует в формировании меню аналитики"""
    default = 0  # Раздел без доп пунктов
    economy = 1  # Раздел с прогнозом КС ЦБ и макроэконом показателями [витрина данных]
    financial_exchange = 2  # Раздел с прогнозом валютных курсов


class ResearchSummaryType(Enum):
    """Тип формирования сводки отчетов CIB Research, участвует в формировании меню аналитики"""
    periodic = 0  # Предлагает пользователю выгрузить отчеты за период
    last_actual = 1  # Выгружает последний актуальный отчет
    analytical_indicators = 2  # Формирует отдельное меню для выгрузки различных аналитических данных
    key_rate_dynamics_table = 3  # Выгрузка таблицы викли пульс с прогнозом КС ЦБ
    exc_rate_prediction_table = 4  # Выгрузка таблицы викли пульс с прогнозом валют
    data_mart = 5  # Выгрузка витрины данных
    economy_monthly = 6  # Выгрузка ежемесячных обзоров по экономике РФ
    economy_daily = 7  # Выгрузка ежедневных обзоров по экономике РФ


class FIGroupType(Enum):
    bonds = 0, 'ОФЗ'
    # obligates = 1, 'Корпоративные облигации '
    # foreign_markets = 2, 'Зарубежные рынки '

    def __init__(self, value, title):
        self._value_ = value
        self._title_ = title

    @property
    def title(self):
        return self._title_


class IndustryTypes(IntEnum):
    """Типы отраслей. Используется для меню отраслевой аналитики и для таблицы bot_industry_documents"""
    default = auto()            # Все стандартные отрасли
    other = auto()              # Пункт прочее
    general_comments = auto()   # Пункт общий комментарий


class SubjectType(str, Enum):
    """Типы объектов, по которым собираются новости."""

    client = 'client'
    commodity = 'commodity'
    industry = 'industry'
