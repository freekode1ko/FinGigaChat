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


def get_feedback_regenerate_kb(rephrase_query: bool = False, initially_query: bool = False) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру для отправки обратной связи с кнопкой перегенерации ответа.

    Формат:
    [ 👍 ][ 👎 ][ 🔄 ]

    :param rephrase_query:      Использовать для генерации ответа перефразированный вопрос.
    :param initially_query:     Использовать для генерации ответа изначальный вопрос пользователя.
    """
    call_data = RegenerateResponse(rephrase_query=rephrase_query, initially_query=initially_query).pack()

    kb = get_feedback_kb(as_markup=False)
    kb.add(types.InlineKeyboardButton(text=dict_of_emoji['regenerate'], callback_data=call_data))
    return kb.as_markup()
