"""Колбеки для аналитики"""
from aiogram.filters.callback_data import CallbackData

from constants import analytics as callback_prefixes


class AnalyticsMenu(CallbackData, prefix=callback_prefixes.MENU):
    """CallbackData для меню аналитики"""

    pass
