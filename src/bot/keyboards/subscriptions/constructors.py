from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_approve_action_kb(yes_callback: str, no_callback: str, back_callback: str) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Да ][ Нет ]
    [   назад   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data=yes_callback))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data=no_callback))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=back_callback))
    return keyboard.as_markup()
