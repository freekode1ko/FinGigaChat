from aiogram.filters.callback_data import CallbackData

from constants.products import hot_offers as callback_prefixes


class Menu(CallbackData, prefix=callback_prefixes.MENU):
    pass


class GetHotOffersPDF(CallbackData, prefix=callback_prefixes.GET_HOT_OFFERS_PDF):
    """Отправка пдф файлов по hot offers"""
    group_id: int
