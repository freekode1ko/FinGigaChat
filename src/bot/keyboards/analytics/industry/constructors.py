"""Клавиатуры для отрасли"""
import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.analytics import constructors
from keyboards.analytics.industry import callbacks


def get_menu_kb(item_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]

    :param item_df: DataFrame[id, name]
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in item_df.iterrows():
        keyboard.row(types.InlineKeyboardButton(
            text=item['name'],
            callback_data=callbacks.Menu(
                menu=callbacks.MenuEnum.get_industry_anal,
                industry_id=item['id'],
                industry_type=item['type'],
            ).pack()),
        )

    return constructors.get_sub_menu_kb(keyboard)
