from aiogram.filters.callback_data import CallbackData

from constants import products as callback_prefixes


class ProductsMenu(CallbackData, prefix=callback_prefixes.MENU):
    pass
