from typing import Optional

from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from constants.products import state_support
from db import models
from handlers.products import callbacks


def get_sub_menu_kb(
        items: list[models.Product],
        format_type: callbacks.FormatType,
        back_callback_data: Optional[str] = None,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ продукт 1 ]
    ...
    [ продукт n ]
    [  назад  ]

    :param items: список models.Product с информацией о продуктах
    :param format_type: Объект, который создает данные для callback
    :param back_callback_data: callback_data для кнопки назад
    """
    keyboard = InlineKeyboardBuilder()

    for item in items:
        item_callback = callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.get_product_documents,
            group_id=item.group_id,
            format_type=format_type,
            product_id=item.id,
        )

        keyboard.row(types.InlineKeyboardButton(
            text=item.name,
            callback_data=item_callback.pack()),
        )

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=back_callback_data or callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.main_menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_menu_kb(groups: list[models.ProductGroup]) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Hot offers ]
    [ Продуктовая полка ]
    [ Господдержка ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()

    for group in groups:
        keyboard.row(types.InlineKeyboardButton(
            text=group.name,
            callback_data=callbacks.ProductsMenuData(
                menu=callbacks.ProductsMenusEnum.group_products,
                group_id=group.id,
                format_type=(callbacks.FormatType.group_files if group.name_latin != 'hot_offers'
                             else callbacks.FormatType.individual_messages),
            ).pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=state_support.TITLE,
        callback_data=callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.state_support,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()
