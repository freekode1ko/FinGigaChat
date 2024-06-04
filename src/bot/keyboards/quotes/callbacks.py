from aiogram.filters.callback_data import CallbackData

from constants import quotes as callback_prefixes


class QuotesMenu(CallbackData, prefix=callback_prefixes.MENU):
    """Меню котировки"""

    pass


class FX(CallbackData, prefix=callback_prefixes.FX):
    """валютный рынок"""

    pass


class FI(CallbackData, prefix=callback_prefixes.FI):
    """долговой рынок"""

    pass


class Equity(CallbackData, prefix=callback_prefixes.EQUITY):
    """рынок акций"""

    pass


class Commodities(CallbackData, prefix=callback_prefixes.COMMODITIES):
    """Ставки"""

    pass


class Eco(CallbackData, prefix=callback_prefixes.ECO):
    """товарный рынок"""

    pass


class GetFIItemData(CallbackData, prefix=callback_prefixes.GET_FI_ITEM_DATA):
    """Получение инфы по финансовому инструменту"""

    item_id: int
    type: int
