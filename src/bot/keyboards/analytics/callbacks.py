from aiogram.filters.callback_data import CallbackData

from constants import analytics as callback_prefixes


class AnalyticsMenu(CallbackData, prefix=callback_prefixes.MENU):
    pass
