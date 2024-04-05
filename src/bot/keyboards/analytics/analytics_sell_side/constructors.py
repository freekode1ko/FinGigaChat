from typing import Any

import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import analytics
from keyboards.analytics import constructors
from keyboards.analytics.analytics_sell_side import callbacks


def get_menu_kb(group_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]

    :param group_df: DataFrame[id, name] инфа о группах CIB Research
    """
    return constructors.get_sub_menu_kb(group_df, callbacks.GetCIBGroupSections)


def get_sections_by_group_menu_kb(
        section_df: pd.DataFrame,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Раздел 1 ]
    ...
    [ Раздел n ]
    [  назад  ]

    :param group_info: dict[id, name] инфа о группе CIB Research
    :param section_df: DataFrame[id, name, dropdown_flag, is_subscribed] инфа о разделах CIB Research
    """
    keyboard = InlineKeyboardBuilder()

    for index, item in section_df.iterrows():
        button_txt = item['name'].capitalize()
        section_callback = callbacks.GetCIBSectionResearches(section_id=item['id'])

        keyboard.row(types.InlineKeyboardButton(
            text=button_txt,
            callback_data=section_callback.pack()),
        )

    keyboard.row(types.InlineKeyboardButton(
        text='Назад',
        callback_data=callbacks.Menu().pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Завершить',
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()


def get_research_types_by_section_menu_kb(
        group_id: int,
        research_types_df: pd.DataFrame,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [][ отчет 1 ]
    ...
    [][ отчет n ]
    [   назад   ]

    :param group_id: id группы CIB Research
    :param research_types_df: DataFrame[id, name, is_signed] инфа о подборке подписок
    """
    keyboard = InlineKeyboardBuilder()

    for index, item in research_types_df.iterrows():
        research_type_callback = callbacks.GetCIBResearchType(research_type_id=item['id'])
        button_txt = item["name"].capitalize()
        keyboard.row(types.InlineKeyboardButton(text=button_txt, callback_data=research_type_callback.pack()))

    keyboard.row(types.InlineKeyboardButton(
        text='Назад',
        callback_data=callbacks.GetCIBGroupSections(group_id=group_id).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Завершить',
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()


def get_select_period_kb(item_id: int, section_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора периода, за который пользователь получит сводку новостей

    :param item_id: id объекта, по которому идет выгрузка данных
    :param section_id: id раздела, в котором только что был пользователь
    return: Клавиатура с кнопками
            1а) за 1 день
            1б) за 3 дня
            2) за неделю
            3) за месяц
            4) назад
            5) Завершить
    """
    keyboard = InlineKeyboardBuilder()

    periods_list = [
        {
            'text': 'За 1 день',
            'days': 1,
        },
        {
            'text': 'За 3 дня',
            'days': 3,
        },
        {
            'text': 'За неделю',
            'days': 7,
        },
        {
            'text': 'За месяц',
            'days': 30,  # average
        },
    ]

    for period in periods_list:
        by_days = callbacks.GetResearchesOverDays(
            research_type_id=item_id,
            days_count=period['days'],
        )

        keyboard.row(types.InlineKeyboardButton(text=period['text'], callback_data=by_days.pack()))
    keyboard.row(types.InlineKeyboardButton(
        text='Назад',
        callback_data=callbacks.GetCIBSectionResearches(section_id=section_id).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Завершить',
        callback_data=analytics.END_MENU,
    ))

    return keyboard.as_markup()
