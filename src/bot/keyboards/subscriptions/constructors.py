from typing import Type

import pandas as pd
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from constants.subscriptions import const
from constants.subscriptions import research
from constants.subscriptions.news import telegram
from constants.subscriptions.news import client
from constants.subscriptions.news import commodity
from constants.subscriptions.news import industry


def get_approve_action_kb(yes_callback: str, no_callback: str, back_callback: str) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Да ][ Нет ]
    [   назад   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data=yes_callback))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data=no_callback))
    keyboard.row(types.InlineKeyboardButton(text=constants.BACK_BUTTON_TXT, callback_data=back_callback))
    return keyboard.as_markup()


def get_subscriptions_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Новости ]
    [ Аналитика  ]
    [ Завершить  ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Новости', callback_data=const.NEWS_SUBS_MENU))
    keyboard.row(types.InlineKeyboardButton(text='Аналитика', callback_data=research.GET_CIB_RESEARCH_SUBS_MENU))
    keyboard.row(types.InlineKeyboardButton(text=constants.END_BUTTON_TXT, callback_data=const.END_WRITE_SUBS))
    return keyboard.as_markup()


def get_news_subscriptions_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Подписки на клиентов, сырье, отрасли ]
    [ Подписки на телеграм-каналы  ]
    [ Назад  ]
    [ Завершить  ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Подписки на клиентов',
        callback_data=client.CLIENT_SUBS_MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Подписки на сырьевые товары',
        callback_data=commodity.COMMODITY_SUBS_MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Подписки на отрасли',
        callback_data=industry.INDUSTRY_SUBS_MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Подписки на телеграм-каналы',
        callback_data=telegram.TG_MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(text=constants.BACK_BUTTON_TXT, callback_data=const.SUBS_MENU))
    keyboard.row(types.InlineKeyboardButton(text=constants.END_BUTTON_TXT, callback_data=const.END_WRITE_SUBS))
    return keyboard.as_markup()
