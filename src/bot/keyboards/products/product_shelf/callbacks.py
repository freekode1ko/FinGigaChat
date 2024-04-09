from aiogram.filters.callback_data import CallbackData

from constants.products import product_shelf as callback_prefixes


class Menu(CallbackData, prefix=callback_prefixes.MENU):
    pass


class GetGroupPDF(CallbackData, prefix=callback_prefixes.GET_PRODUCT_PDF):
    """Выгрузка пдф файлов по группе (продуктовая полка)"""
    group_id: int
