"""Фабрики колбэк данных для меню аналитики"""
from aiogram.filters.callback_data import CallbackData

from constants import analytics as callback_prefixes


class AnalyticsMenu(CallbackData, prefix=callback_prefixes.MENU):
    """Главное меню Аналитики"""


class GetFullResearch(CallbackData, prefix=callback_prefixes.GET_FULL_RESEARCH):
    """Колбэк данные для кнопки получения полной версии отчета"""

    research_id: int
