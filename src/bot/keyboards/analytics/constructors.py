from typing import Type

import pandas as pd
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import analytics
from constants.analytics import analytics_sell_side
from constants.analytics import industry
from constants.analytics import macro_view


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

    for index, item in group_df.iterrows():
        get_group_sections_callback = callback_factory(
            group_id=item['id'],
        )

        keyboard.row(types.InlineKeyboardButton(
            text=item['name'].capitalize(),
            callback_data=get_group_sections_callback.pack()),
        )

    keyboard.row(types.InlineKeyboardButton(
        text='Назад',
        callback_data=analytics.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Завершить',
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()


def get_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Аналитика sell-side ]
    [ Отраслевая аналитика ]
    [ MacroView ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Аналитика sell-side',
        callback_data=analytics_sell_side.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Отраслевая аналитика',
        callback_data=industry.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='MacroView',
        callback_data=macro_view.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Завершить',
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()
