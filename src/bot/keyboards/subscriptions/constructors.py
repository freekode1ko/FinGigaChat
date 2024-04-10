from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import subscriptions as callback_prefixes, constants


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
    keyboard.row(types.InlineKeyboardButton(text='Новости', callback_data=callback_prefixes.NEWS_SUBS_MENU))
    keyboard.row(types.InlineKeyboardButton(text='Аналитика', callback_data=callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU))
    keyboard.row(types.InlineKeyboardButton(text=constants.END_BUTTON_TXT, callback_data=callback_prefixes.END_WRITE_SUBS))
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
        text='Подписки на клиентов, сырье, отрасли',
        callback_data=callback_prefixes.CLIENT_SUBS_MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Подписки на телеграм-каналы',
        callback_data=callback_prefixes.TG_MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(text=constants.BACK_BUTTON_TXT, callback_data=callback_prefixes.SUBS_MENU))
    keyboard.row(types.InlineKeyboardButton(text=constants.END_BUTTON_TXT, callback_data=callback_prefixes.END_WRITE_SUBS))
    return keyboard.as_markup()
