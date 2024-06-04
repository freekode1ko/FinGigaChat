from aiogram.filters.callback_data import CallbackData

from constants import analytics as callback_prefixes


class AnalyticsMenu(CallbackData, prefix=callback_prefixes.MENU):
    pass


class GetFullResearch(CallbackData, prefix=callback_prefixes.GET_FULL_RESEARCH):
    research_id: int
