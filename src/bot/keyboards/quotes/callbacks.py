from aiogram.filters.callback_data import CallbackData

from constants import quotes as callback_prefixes


class QuotesMenu(CallbackData, prefix=callback_prefixes.MENU):
    pass


class FX(CallbackData, prefix=callback_prefixes.FX):
    pass


class FI(CallbackData, prefix=callback_prefixes.FI):
    pass


class Equity(CallbackData, prefix=callback_prefixes.EQUITY):
    pass


class Commodities(CallbackData, prefix=callback_prefixes.COMMODITIES):
    pass


class Eco(CallbackData, prefix=callback_prefixes.ECO):
    pass


class GetFIItemData(CallbackData, prefix=callback_prefixes.GET_FI_ITEM_DATA):
    item_id: int
    type: int
