"""Фабрики колбэк данных для меню аналитики"""
from aiogram.filters.callback_data import CallbackData

from constants import analytics as callback_prefixes


class AnalyticsMenu(CallbackData, prefix=callback_prefixes.MENU):
    """CallbackData для Главное меню Аналитики"""


class GetFullResearch(CallbackData, prefix=callback_prefixes.GET_FULL_RESEARCH):
    """CallbackData для кнопки получения полной версии отчета"""

    research_id: int
