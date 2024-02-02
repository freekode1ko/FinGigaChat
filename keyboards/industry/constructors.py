import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants.bot.constants import SELECTED, UNSELECTED
from constants.bot.industry import ALL_TG_CHANNELS_CALLBACK_TEXT, MY_TG_CHANNELS_CALLBACK_TEXT, BACK_TO_MENU
from keyboards.industry.callbacks import SelectNewsPeriod, GetNewsDaysCount


def get_industry_kb(industry_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора отрасли, по которой пользователь хочет получить сводку новостей

    :param industry_df: DataFrame[[id, name]] с данными об отраслях из БД
    return: Клавиатура с выбором отраслей
    """
    keyboard = InlineKeyboardBuilder()

    for index, industry in industry_df.iterrows():
        callback_meta = SelectNewsPeriod(
            industry_id=industry['id'],
            my_subscriptions=True,
        )
        keyboard.row(types.InlineKeyboardButton(text=industry['name'].title(), callback_data=callback_meta.pack()))
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
    by_my_subs = SelectNewsPeriod(
        industry_id=industry_id,
        my_subscriptions=True,
    )
    by_all_subs = SelectNewsPeriod(
        industry_id=industry_id,
        my_subscriptions=False,
    )
    get_by_my_subs_text = f'{MY_TG_CHANNELS_CALLBACK_TEXT}{SELECTED if my_subscriptions else UNSELECTED}'
    get_by_all_subs_text = f'{ALL_TG_CHANNELS_CALLBACK_TEXT}{SELECTED if not my_subscriptions else UNSELECTED}'
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
        by_days = GetNewsDaysCount(
            industry_id=industry_id,
            my_subscriptions=my_subscriptions,
            days_count=period['days'],
        )

        keyboard.row(types.InlineKeyboardButton(text=period['text'], callback_data=by_days.pack()))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=BACK_TO_MENU))

    return keyboard.as_markup()
