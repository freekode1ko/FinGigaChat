"""Колбеки комодов"""
from enum import auto, IntEnum

from aiogram.filters.callback_data import CallbackData

MENU = 'products_menu'


class CommodityMenusEnum(IntEnum):
    """Enum`сы для меню"""

    commodity_menu = auto()
    news = auto()
    quotes = auto()
    choice_period = auto()
    close = auto()


class CommodityMenuData(CallbackData, prefix=MENU):
    """Данные для меню комодов"""

    menu: CommodityMenusEnum = CommodityMenusEnum.commodity_menu
    commodity_id: int = 0
    days_count: int = 0
