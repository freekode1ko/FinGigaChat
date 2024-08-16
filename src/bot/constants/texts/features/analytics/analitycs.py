"""Модуль для текстовок аналитики."""
from pydantic_settings import BaseSettings


class AnalyticsTexts(BaseSettings):
    """Класс для текстовок аналитики."""

    ANAL_CHOOSE_PUBLIC_MARKET: str = (
        'Аналитика публичных рынков\n'
        'Выберите раздел'
    )

    ANAL_SHOW_PUBLIC_MARKET: str = (
        'Аналитика публичных рынков\n'
        'Раздел "{section}":'  # FIXME text
    )

    ANAL_CHOOSE_INDUSTRY: str = (
        'Выберете отрасль клиента, '
        'по которому вы хотели бы получить данные из SberCIB Investment Research'
    )

    ANAL_CHOOSE_PERIOD: str = (
        'Выберите период, за который хотите получить отчеты по '
        '<b>{research}</b>\n\n'
    )

    ANAL_NOT_REPORT: str = 'На текущий момент, отчеты временно отсутствуют'

    ANAL_WHAT_DATA: str = 'Какие данные вас интересуют по клиенту <b>{research}</b>?'

    ANAL_NAVI_LINK: str = '<a href="{link}">Цифровая справка клиента: "{research}"</a>'

    ANAL_NOT_NAVI_LINK: str = 'Цифровая справка по клиенту "{research}" отсутствует'

    ANAL_FULL_VERSION_REPORT: str = 'Полная версия отчета: <b>{header}</b>'

    ANAL_END: str = 'Просмотр аналитики завершен'

    ANAL_START: str = (
        'В этом разделе вы можете получить, всесторонний анализ российского финансового рынка '
        'от SberCIB Investment Research'
    )
