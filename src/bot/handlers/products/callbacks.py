"""Колбеки продуктов"""
from enum import auto, IntEnum

from aiogram.filters.callback_data import CallbackData

MENU = 'products_menu'


class ProductsMenusEnum(IntEnum):
    """Enum`сы для меню продуктов"""

    # Меню продукты
    main_menu = auto()
    end_menu = auto()

    # меню с продуктами в группе
    group_products = auto()

    # выдача господдержки
    state_support = auto()

    # выдача информации по продукту (файлы и предложения)
    get_product_documents = auto()


class ProductsMenuData(CallbackData, prefix=MENU):
    """Данные для меню продуктов"""

    menu: ProductsMenusEnum = ProductsMenusEnum.main_menu
    product_id: int = 0
    # Эту часть можно унести в redis, чтоб не бояться, что len(ProductsMenuData.pack().encode()) будет > 64
    root_id: int = 0
    back_menu: str | None = ''  # это мем, но приходится писать | None, чтоб тут можно было пустую строку передать, иначе ошибка
