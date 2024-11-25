"""Клавиатуры для котировок"""
from aiogram.filters.callback_data import CallbackData

from constants import quotes as callback_prefixes
from constants.enums import QuotesType


class QuotesMenu(CallbackData, prefix=callback_prefixes.MENU):
    """Меню котировки"""

    pass


class FX(CallbackData, prefix=QuotesType.FX):
    """валютный рынок"""

    pass


class FI(CallbackData, prefix=QuotesType.FI):
    """долговой рынок"""

    pass


class Equity(CallbackData, prefix=QuotesType.EQUITY):
    """рынок акций"""

    pass


class Commodities(CallbackData, prefix=QuotesType.COMMODITIES):
    """Ставки"""

    pass


class Eco(CallbackData, prefix=QuotesType.ECO):
    """товарный рынок"""

    pass


class GetFIItemData(CallbackData, prefix=callback_prefixes.GET_FI_ITEM_DATA):
    """Получение инфы по финансовому инструменту"""

    item_id: int
    type: int
