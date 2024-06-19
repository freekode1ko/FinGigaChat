"""Колбеки продуктов"""
from enum import auto, IntEnum

from aiogram.filters.callback_data import CallbackData


MENU = 'products_menu'


class FormatType(IntEnum):
    """Enum`сы форматов"""

    # Выдача общего текста группы и затем выдача группы файлов
    group_files = 1
    # Выдача общего текста группы, затем для каждого документа выдача сообщений:
    # document.name жирным
    # document.description просто текст
    # [document.file] если есть файл
    individual_messages = 2


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
    format_type: FormatType = FormatType.group_files
    group_id: int = 0
    product_id: int = 0
