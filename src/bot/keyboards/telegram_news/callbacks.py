"""CallbackData на новости с тг каналов"""
from aiogram.filters.callback_data import CallbackData

from constants import industry as callback_prefixes


class SelectNewsPeriod(CallbackData, prefix=callback_prefixes.SELECTED_INDUSTRY_TOKEN):
    """Меню выбора раздела для получения сводки новостей по тг каналам за период"""

    section_id: int
    my_subscriptions: bool


class GetNewsDaysCount(CallbackData, prefix=callback_prefixes.GET_INDUSTRY_TG_NEWS):
    """Меню выбора периода для получения сводки новостей по тг каналам"""

    section_id: int
    my_subscriptions: bool
    days_count: int
