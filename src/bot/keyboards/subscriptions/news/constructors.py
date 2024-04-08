from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import subscriptions as callback_prefixes
from keyboards.subscriptions import constructors


def get_prepare_subs_delete_all_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Да ][ Нет ]
    [   назад   ]
    """
    return constructors.get_approve_action_kb(
        callback_prefixes.CLIENT_SUBS_DELETE_ALL_DONE,
        callback_prefixes.CLIENT_SUBS_MENU,
        callback_prefixes.CLIENT_SUBS_MENU,
    )


def get_back_to_client_subs_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [   назад в меню   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.CLIENT_SUBS_MENU))
    return keyboard.as_markup()


def get_client_subscriptions_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Список активных подписок ]
    [ Добавить новые подписки  ]
    [ Удалить подписки  ]
    [ Удалить все подписки ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Список активных подписок', callback_data='myactivesubscriptions'))
    keyboard.row(types.InlineKeyboardButton(text='Добавить новые подписки', callback_data='addnewsubscriptions'))
    keyboard.row(types.InlineKeyboardButton(text='Удалить подписки', callback_data='deletesubscriptions'))
    keyboard.row(types.InlineKeyboardButton(text='Удалить все подписки', callback_data='deleteallsubscriptions'))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.NEWS_SUBS_MENU))
    keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data=callback_prefixes.END_WRITE_SUBS))
    return keyboard.as_markup()
