"""Клавиатуры для рага"""
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from configs.config import dict_of_emoji
from keyboards.rag.callbacks import GetReports, RegenerateResponse


def get_feedback_kb(as_markup: bool = True, with_reports: bool = False) -> InlineKeyboardMarkup | InlineKeyboardBuilder:
    """
    Формирует Inline клавиатуру для отправки обратной связи от пользователя.

    Формат:
    [ 👍 ][ 👎 ]

    :param as_markup:       Флаг для преобразования клавиатуры в разметку.
    :param with_reports:    Использовались ли обзоры из Research для генерации ответа.
    :return:                Builder для последующей модификации клавиатуры
                            или разметку для прикрепления клавиатуры к сообщению.
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text=dict_of_emoji['like'], callback_data='like'))
    keyboard.add(types.InlineKeyboardButton(text=dict_of_emoji['dislike'], callback_data='dislike'))
    if as_markup:
        keyboard = get_button_for_full_researches_kb(keyboard, with_reports)
        return keyboard.as_markup()
    return keyboard


def get_feedback_regenerate_kb(
        rephrase_query: bool = False,
        initially_query: bool = False,
        with_reports: bool = False,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру для отправки обратной связи с кнопкой перегенерации ответа.

    Формат:
    [ 👍 ][ 👎 ][ 🔄 ]

    :param rephrase_query:      Использовать для генерации ответа перефразированный вопрос.
    :param initially_query:     Использовать для генерации ответа изначальный вопрос пользователя.
    :param with_reports:        Использовались ли обзоры из Research для генерации ответа.
    :return:                    Разметку для прикрепления клавиатуры к сообщению.
    """
    call_data = RegenerateResponse(rephrase_query=rephrase_query, initially_query=initially_query).pack()
    kb = get_feedback_kb(as_markup=False)
    kb.add(types.InlineKeyboardButton(text=dict_of_emoji['regenerate'], callback_data=call_data))
    kb = get_button_for_full_researches_kb(kb, with_reports)
    return kb.as_markup()


def get_button_for_full_researches_kb(kb: InlineKeyboardBuilder, with_reports: bool = False) -> InlineKeyboardBuilder:
    """
    Получить клавиатуру с кнопкой по отображению используемых отчетов при генерации ответа РАГ.

    :param kb:            Генератор клавиатуры.
    :param with_reports:  Использовались ли обзоры из Research для генерации ответа.
    :return:              Генератор с новой кнопкой для получения обзоров или без нее, если обзоры не использовались.
    """
    if with_reports:
        kb.row(types.InlineKeyboardButton(text='Получить полные отчеты', callback_data=GetReports().pack()))
    return kb
