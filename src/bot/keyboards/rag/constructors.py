from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from configs.config import dict_of_emoji
from keyboards.rag.callbacks import RegenerateResponse


def get_feedback_kb(as_markup: bool = True) -> InlineKeyboardMarkup | InlineKeyboardBuilder:
    """
    Формирует Inline клавиатуру для отправки обратной связи от пользователя.

    Формат:
    [ 👍 ][ 👎 ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text=dict_of_emoji['like'], callback_data='like'))
    keyboard.add(types.InlineKeyboardButton(text=dict_of_emoji['dislike'], callback_data='dislike'))
    return keyboard.as_markup() if as_markup else keyboard


def get_feedback_regenerate_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру для отправки обратной связи с кнопкой перегенерации ответа.

    Формат:
    [ 👍 ][ 👎 ][ 🔄 ]
    """
    kb = get_feedback_kb(as_markup=False)
    kb.add(types.InlineKeyboardButton(text=dict_of_emoji['regenerate'], callback_data=RegenerateResponse().pack()))
    return kb.as_markup()
