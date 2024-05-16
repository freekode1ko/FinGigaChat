from aiogram.filters.callback_data import CallbackData

from constants import industry as callback_prefixes


class SelectNewsPeriod(CallbackData, prefix=callback_prefixes.SELECTED_INDUSTRY_TOKEN):
    section_id: int
    my_subscriptions: bool


class GetNewsDaysCount(CallbackData, prefix=callback_prefixes.GET_INDUSTRY_TG_NEWS):
    section_id: int
    my_subscriptions: bool
    days_count: int
