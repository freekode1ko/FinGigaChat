"""Клавиатуры для главного меню в Меню Аналитика"""
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import analytics, constants
from constants.analytics import analytics_sell_side
from constants.analytics import macro_view
from keyboards.analytics import callbacks
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


def get_full_research_kb(research_id: int) -> InlineKeyboardMarkup:
    """
    Получить клавиатуру для выдачи полной версии отчета.

    :param research_id: research.id, который будет выдан при нажатии на кнопку
    :return: Клавиатура вида
    [ Получить полную версию ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Получить полную версию',
        callback_data=callbacks.GetFullResearch(research_id=research_id).pack(),
    ))
    return keyboard.as_markup()


def get_few_full_research_kb(
        kb: InlineKeyboardBuilder,
        reports_data: list[dict[str, str | int]] | None,
) -> InlineKeyboardMarkup:
    """
    Получить клавиатуру для выдачи полной версии нескольких отчетов.

    :param kb:           Генератор клавиатуры.
    :param reports_data: Список из словарей с данными об обзорах {'header': ..., 'research_id': ...}
    :return:             Клавиатура с новыми кнопками для получения обзоров.
    """
    if not reports_data:
        return kb.as_markup()

    added_ids = set()
    for r_data in reports_data:
        if (research_id := r_data['research_id']) in added_ids:
            continue
        added_ids.add(research_id)
        kb.row(types.InlineKeyboardButton(
            text=r_data['header'].split('. ', 1)[0],
            callback_data=callbacks.GetFullResearch(research_id=research_id).pack(),
        ))

    return kb.as_markup()
