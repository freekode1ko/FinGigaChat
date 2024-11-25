"""Клавиатуры для котировок"""
from ast import literal_eval
from typing import Type

import pandas as pd
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


from configs import config
from constants import constants, enums, quotes
from constants.texts import texts_manager


def get_sub_menu_kb(item_df: pd.DataFrame, callback_factory: Type[CallbackData]) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]

    :param item_df: DataFrame[id, name, type] инфа о группах CIB Research
    :param callback_factory: Объект, который создает данные для callback
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in item_df.iterrows():
        get_group_sections_callback = callback_factory(
            item_id=item['id'],
            type=item['type'],
        )

        keyboard.row(types.InlineKeyboardButton(
            text=item['name'],
            callback_data=get_group_sections_callback.pack()),
        )

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=quotes.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=quotes.END_MENU,
    ))
    return keyboard.as_markup()


def get_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ FX ]
    [ FI ]
    [ Equity ]
    [ Commodities ]
    [ Ставки ]
    [ Web-app ]   /quotes
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='FX',
        callback_data=enums.QuotesType.FX,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='FI',
        callback_data=enums.QuotesType.FI,
    ))
    # keyboard.row(types.InlineKeyboardButton(
    #     text='Equity',
    #     callback_data=enums.QuotesType.EQUITY,
    # ))
    keyboard.row(types.InlineKeyboardButton(
        text='Commodities',
        callback_data=enums.QuotesType.COMMODITIES,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Ставки',
        callback_data=enums.QuotesType.ECO,
    ))
    if literal_eval(texts_manager.WEBAPP_SHOW_BUTTONS):
        keyboard.row(types.InlineKeyboardButton(
            text='🔥New! Мини-приложение',
            web_app=WebAppInfo(url=f'{config.WEB_APP_URL}/quotes')
        ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=quotes.END_MENU,
    ))
    return keyboard.as_markup()
