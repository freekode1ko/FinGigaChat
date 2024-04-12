import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from constants import industry as callback_prefixes
from keyboards.industry import callbacks


def get_industry_kb(industry_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора отрасли, по которой пользователь хочет получить сводку новостей

    :param industry_df: DataFrame[[id, name]] с данными об отраслях из БД
    return: Клавиатура с выбором отраслей
    """
    keyboard = InlineKeyboardBuilder()

    for index, industry in industry_df.iterrows():
        callback_meta = callbacks.SelectNewsPeriod(
            industry_id=industry['id'],
            my_subscriptions=True,
        )
        keyboard.row(types.InlineKeyboardButton(text=industry['name'].capitalize(), callback_data=callback_meta.pack()))
    return keyboard.as_markup()


def get_select_period_kb(industry_id: int, my_subscriptions: bool = True) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора периода, за который пользователь получит сводку новостей

    :param industry_id: id отрасли из БД
    :param my_subscriptions: Флаг, что выбран способ получения новостей из моих подписок (True) или из всех каналов (False)
    return: Клавиатура с кнопками
            1а) по подпискам (галка, по умолчанию)
            1б) по всем каналам
            2а) за 1 день
            2б) за 3 дня
            3) за неделю
            4) за месяц
            5) назад
    """
    keyboard = InlineKeyboardBuilder()
    by_my_subs = callbacks.SelectNewsPeriod(
        industry_id=industry_id,
        my_subscriptions=True,
    )
    by_all_subs = callbacks.SelectNewsPeriod(
        industry_id=industry_id,
        my_subscriptions=False,
    )
    is_by_my_subs = constants.SELECTED if my_subscriptions else constants.UNSELECTED
    is_by_all_subs = constants.SELECTED if not my_subscriptions else constants.UNSELECTED
    get_by_my_subs_text = f'{callback_prefixes.MY_TG_CHANNELS_CALLBACK_TEXT}{is_by_my_subs}'
    get_by_all_subs_text = f'{callback_prefixes.ALL_TG_CHANNELS_CALLBACK_TEXT}{is_by_all_subs}'
    keyboard.add(types.InlineKeyboardButton(text=get_by_my_subs_text, callback_data=by_my_subs.pack()))
    keyboard.add(types.InlineKeyboardButton(text=get_by_all_subs_text, callback_data=by_all_subs.pack()))

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
        by_days = callbacks.GetNewsDaysCount(
            industry_id=industry_id,
            my_subscriptions=my_subscriptions,
            days_count=period['days'],
        )

        keyboard.row(types.InlineKeyboardButton(text=period['text'], callback_data=by_days.pack()))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_prefixes.BACK_TO_MENU,
    ))

    return keyboard.as_markup()
