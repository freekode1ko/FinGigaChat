from typing import Any, Type

import pandas as pd
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import analytics, enums, constants
from keyboards.analytics import constructors
from keyboards.analytics.analytics_sell_side import callbacks


def get_menu_kb(item_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]
    [   Завершить   ]

    :param item_df: DataFrame[name, callback_data] инфа о группах/разделах CIB Research
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in item_df.iterrows():
        keyboard.row(types.InlineKeyboardButton(
            text=item['name'],
            callback_data=item['callback_data']),
        )

    return constructors.get_sub_menu_kb(keyboard)


def get_sections_by_group_menu_kb(
        section_df: pd.DataFrame,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Раздел 1 ]
    ...
    [ Раздел n ]
    [  назад  ]
    [   Завершить   ]

    :param group_info: dict[id, name] инфа о группе CIB Research
    :param section_df: DataFrame[id, name, dropdown_flag, is_subscribed] инфа о разделах CIB Research
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in section_df.iterrows():
        button_txt = item['name'].capitalize()
        section_callback = callbacks.GetCIBSectionResearches(section_id=item['id'])

        keyboard.row(types.InlineKeyboardButton(
            text=button_txt,
            callback_data=section_callback.pack()),
        )

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callbacks.Menu().pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()


def get_research_types_by_section_menu_kb(
        section_info: dict[str, Any],
        research_types_df: pd.DataFrame,
        back_callback_data: str,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [][ отчет 1 ]
    ...
    [][ отчет n ]
    [   назад   ]
    [   Завершить   ]

    :param section_info: dict[id раздела CIB Research, section_type, research_group_id id группы CIB Research]
    :param research_types_df: DataFrame[id, name, is_subscribed, summary_type] инфа о подборке подписок
    :param back_callback_data: Данные для кнопки Назад
    """
    keyboard = InlineKeyboardBuilder()

    # update research_type_df by section_type (add weekly pulse, view)
    match section_info['section_type']:
        case enums.ResearchSectionType.economy.value:
            # add weekly pulse прогноз динамики КС ЦБ
            # add view
            economy_research_type_id = research_types_df.loc[0, 'id']
            extra_rows = pd.DataFrame(
                [
                    [0, 'Прогноз по ключевой ставке', False, enums.ResearchSummaryType.key_rate_dynamics_table],
                    [economy_research_type_id, 'Ежемесячные обзоры', False, enums.ResearchSummaryType.economy_monthly],
                    [economy_research_type_id, 'Ежедневные обзоры', False, enums.ResearchSummaryType.economy_daily],
                    [0, 'Макроэкономические показатели', False, enums.ResearchSummaryType.data_mart],
                ],
                columns=['id', 'name', 'is_subscribed', 'summary_type'],
            )
            research_types_df = None
        case enums.ResearchSectionType.financial_exchange.value:
            # add weekly pulse прогноз валютных курсов
            extra_rows = pd.DataFrame(
                [
                    [0, 'Прогноз валютных курсов', False, enums.ResearchSummaryType.exc_rate_prediction_table],
                ],
                columns=['id', 'name', 'is_subscribed', 'summary_type'],
            )
        case _:
            extra_rows = None

    for _, item in pd.concat([extra_rows, research_types_df]).iterrows():
        research_type_callback = callbacks.GetCIBResearchData(
            research_type_id=item['id'],
            summary_type=item['summary_type'],
        )

        button_txt = item["name"]
        keyboard.row(types.InlineKeyboardButton(text=button_txt, callback_data=research_type_callback.pack()))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=back_callback_data,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()


def get_select_period_kb(
        item_id: int,
        callback_factory: Type[CallbackData],
        back_callback: str,
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора периода, за который пользователь получит сводку новостей

    :param item_id: id объекта, по которому идет выгрузка данных
    :param callback_factory: класс формирования callback_data  [research_type_id, days_count]
    :param back_callback: callback_data для кнопки Назад
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
        by_days = callback_factory(
            research_type_id=item_id,
            days_count=period['days'],
        )

        keyboard.row(types.InlineKeyboardButton(text=period['text'], callback_data=by_days.pack()))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=back_callback,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=analytics.END_MENU,
    ))

    return keyboard.as_markup()


def client_analytical_indicators_kb(research_type_info: dict[str, Any]) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Справка ]
    [ Аналитические обзоры ]
    [ P&L модель ]
    [ Модель баланса ]
    [ Модель CF ]
    [ Коэффициенты ]
    [  назад  ]
    [   Завершить   ]

    :param research_type_info: инфа о типе отчета CIB Research dict[id, research_section_id, summary_type]
    """
    keyboard = InlineKeyboardBuilder()

    buttons = [
        # {
        #     'name': 'Цифровая справка',
        #     'callback_data': callbacks.GetINavigatorSource(research_type_id=research_type_info['id']).pack(),
        # },
        {
            'name': 'Аналитические обзоры',
            'callback_data': callbacks.SelectClientResearchesGettingPeriod(
                research_type_id=research_type_info['id'],
                summary_type=research_type_info['summary_type'],
            ).pack(),
        },
        {
            'name': 'P&L модель',
            'callback_data': callbacks.NotImplementedFunctionality(research_type_id=research_type_info['id']).pack(),
        },
        {
            'name': 'Модель баланса',
            'callback_data': callbacks.NotImplementedFunctionality(research_type_id=research_type_info['id']).pack(),
        },
        {
            'name': 'Модель CF',
            'callback_data': callbacks.NotImplementedFunctionality(research_type_id=research_type_info['id']).pack(),
        },
        {
            'name': 'Коэффициенты',
            'callback_data': callbacks.NotImplementedFunctionality(research_type_id=research_type_info['id']).pack(),
        },
    ]

    for item in buttons:
        keyboard.row(types.InlineKeyboardButton(
            text=item['name'],
            callback_data=item['callback_data'],
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callbacks.GetCIBSectionResearches(section_id=research_type_info['research_section_id']).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=analytics.END_MENU,
    ))
    return keyboard.as_markup()
