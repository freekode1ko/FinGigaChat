from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import analytics, constants
from constants.analytics import analytics_sell_side
from constants.analytics import macro_view
from keyboards.analytics.industry import callbacks as industry_callbacks


def get_sub_menu_kb(keyboard: InlineKeyboardBuilder) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]

    :param keyboard: сформированная клавиатура без кнопок завершить и назад
    """
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=analytics.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()


def get_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Аналитика публичных рынков ]
    [ Отраслевая аналитика ]
    [ macro_view.TITLE ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Аналитика публичных рынков',
        callback_data=analytics_sell_side.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Отраслевая аналитика',
        callback_data=industry_callbacks.Menu().pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=macro_view.TITLE,
        callback_data=macro_view.MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()
