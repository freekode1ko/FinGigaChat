"""Модуль для текстовок аналитики sell slide."""
from pydantic_settings import BaseSettings


class AnalyticsSellSide(BaseSettings):
    """Класс для текстовок аналитики sell slide."""

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
