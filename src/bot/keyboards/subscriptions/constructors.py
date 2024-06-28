"""Клавиатуры для подписок"""
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from constants.subscriptions import const
from constants.subscriptions import research
from constants.subscriptions.news import client
from constants.subscriptions.news import commodity
from constants.subscriptions.news import industry
from keyboards.subscriptions.news.telegram import callbacks as telegram_callback_factory


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

    [ Подписки на клиентов ]
    [ Подписки на сырьевые товары ]
    [ Подписки на сырьевые товары ]
    [ Подписки на отрасли ]
    [ Подписки на телеграм-каналы ]
    [ Подписки на аналитические отчеты ]
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
        callback_data=telegram_callback_factory.TelegramSubsMenuData(
            menu=telegram_callback_factory.TelegramSubsMenusEnum.main_menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Подписки на аналитические отчеты',
        callback_data=research.GET_CIB_RESEARCH_SUBS_MENU
    ))
    keyboard.row(types.InlineKeyboardButton(text=constants.END_BUTTON_TXT, callback_data=const.END_WRITE_SUBS))
    return keyboard.as_markup()
