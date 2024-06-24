"""Клавиатуры дял меню продуктов"""

from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import utils.base
from constants import constants
from db import models
from handlers.products import callbacks


def get_sub_menu_kb(
        items: list[models.Product],
        product: models.Product,
        callback_data: callbacks.ProductsMenuData,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ продукт 1 ]
    ...
    [ продукт n ]
    [  назад  ]

    :param items: список models.Product с информацией о продуктах
    :param product: Текущая категория продуктов
    :param callback_data: callback_data текущего меню
    """
    keyboard = InlineKeyboardBuilder()

    for item in items:
        item_callback = callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.group_products,
            product_id=item.id,
            root_id=callback_data.root_id,
            back_menu=callback_data.back_menu,
        )

        keyboard.row(types.InlineKeyboardButton(
            text=item.name,
            callback_data=item_callback.pack()),
        )

    if product.parent_id is not None:
        back_callback_data = (utils.base.unwrap_callback_data(callback_data.back_menu)
                              if callback_data.root_id == callback_data.product_id
                              else callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.group_products,
            product_id=product.parent_id,
            root_id=callback_data.root_id,
            back_menu=callback_data.back_menu,
        ).pack())

        keyboard.row(types.InlineKeyboardButton(
            text=constants.BACK_BUTTON_TXT,
            callback_data=back_callback_data,
        ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_menu_kb(products: list[models.Product]) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Hot offers ]
    [ Продуктовая полка ]
    [ Господдержка ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()

    for product in products:
        keyboard.row(types.InlineKeyboardButton(
            text=product.name,
            callback_data=callbacks.ProductsMenuData(
                menu=callbacks.ProductsMenusEnum.group_products,
                product_id=product.id,
            ).pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()
