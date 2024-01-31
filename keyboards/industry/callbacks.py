from aiogram.filters.callback_data import CallbackData

from constants.bot.industry import SELECTED_INDUSTRY_TOKEN


class SelectNewsPeriod(CallbackData, prefix=SELECTED_INDUSTRY_TOKEN):
    industry_id: int
    my_subscriptions: bool


class GetNewsDaysCount(CallbackData, prefix=SELECTED_INDUSTRY_TOKEN):
    industry_id: int
    my_subscriptions: bool
    days_count: int
