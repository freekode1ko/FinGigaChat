from typing import Type

import pandas as pd
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import products, constants
from constants.products import hot_offers
from constants.products import product_shelf
from constants.products import state_support


def get_sub_menu_kb(group_df: pd.DataFrame, callback_factory: Type[CallbackData]) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]

    :param group_df: DataFrame[id, name] инфа о группах CIB Research
    :param callback_factory: Объект, который создает данные для callback
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in group_df.iterrows():
        get_group_sections_callback = callback_factory(
            group_id=item['id'],
        )

        keyboard.row(types.InlineKeyboardButton(
            text=item['name'],
            callback_data=get_group_sections_callback.pack()),
        )

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=products.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=products.END_MENU,
    ))
    return keyboard.as_markup()


def get_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Hot offers ]
    [ Продуктовая полка ]
    [ Господдержка ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text=hot_offers.TITLE,
        callback_data=hot_offers.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=product_shelf.TITLE,
        callback_data=product_shelf.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=state_support.TITLE,
        callback_data=state_support.GET_STATE_SUPPORT_PDF,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=products.END_MENU,
    ))
    return keyboard.as_markup()
