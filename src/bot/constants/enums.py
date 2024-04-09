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
