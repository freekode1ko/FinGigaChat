from typing import Any, Optional

import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from db import models
from handlers.news import callback_data_factories
from keyboards.base import get_pagination_kb


def get_menu_kb(telegram_groups: list[models.TelegramGroup]) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ телеграм группа 1 ]
    [ ... ]
    [ телеграм группа N ]
    [ Клиентские новости ]
    [ Сырьевые новости ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()

    for telegram_group in telegram_groups:
        keyboard.row(types.InlineKeyboardButton(
            text=telegram_group.name,
            callback_data=callback_data_factories.TelegramGroupData(
                menu=callback_data_factories.NewsMenusEnum.choose_news_subjects,
                back_menu=callback_data_factories.NewsMenusEnum.main_menu,
                telegram_group_id=telegram_group.id,
            ).pack()
        ))

    for news_subject_group in callback_data_factories.NewsItems:
        keyboard.row(types.InlineKeyboardButton(
            text=news_subject_group.title,
            callback_data=callback_data_factories.SubjectData(
                menu=callback_data_factories.NewsMenusEnum.choose_subs_or_unsubs,
                back_menu=callback_data_factories.NewsMenusEnum.main_menu,
                subject=news_subject_group,
            ).pack()
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.NewsMenuData(
            menu=callback_data_factories.NewsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_choose_subs_or_unsubs_kb(subject_data: callback_data_factories.NewsItems) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Выбрать клиента/сырье из списка подписок ]
    [ Выбрать другого клиента/сырье ]
    [ Назад ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()

    for button in subject_data.buttons:
        keyboard.row(types.InlineKeyboardButton(
            text=button['text'],
            callback_data=callback_data_factories.SubjectData(
                menu=callback_data_factories.NewsMenusEnum.subjects_list,
                subscribed=button['subscribed'],
                subject=subject_data.value,
                back_menu=callback_data_factories.NewsMenusEnum.choose_subs_or_unsubs,
            ).pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_data_factories.NewsMenuData(
            menu=callback_data_factories.NewsMenusEnum.main_menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.NewsMenuData(
            menu=callback_data_factories.NewsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_subjects_list_kb(
        page_data: pd.DataFrame,
        current_page: int,
        max_pages: int,
        subscribed: bool,
        subject: callback_data_factories.NewsItems,
) -> InlineKeyboardMarkup:
    """
    [ item 1 ]
    ...
    [ item N ]
    [<-][ Назад ][->]
    [ Завершить ]
    :param page_data:       DataFrame[id, name]
    :param current_page:    текущая страница меню, которую надо отобразить
    :param max_pages:       всего страниц (для блокировки кнопок <- и ->, если достигли начала или конца)
    :param subscribed:      флаг, что выбран клиент из подписок или нет
    :param subject:         группа субъектов (клиенты или сырье)
    """
    page_data['name'] = page_data['name'].str.capitalize()
    page_data['item_callback'] = page_data['id'].apply(
            lambda x: callback_data_factories.SubjectData(
                menu=callback_data_factories.NewsMenusEnum.choose_period_for_subject,
                subject_id=x,
                page=current_page,
                subscribed=subscribed,
                subject=subject,
                back_menu=callback_data_factories.NewsMenusEnum.subjects_list,
            ).pack()
        )
    return get_pagination_kb(
        page_data,
        current_page,
        max_pages,
        next_page_callback=callback_data_factories.SubjectData(
            menu=callback_data_factories.NewsMenusEnum.subjects_list,
            back_menu=callback_data_factories.NewsMenusEnum.choose_subs_or_unsubs,
            page=current_page + 1,
            subscribed=subscribed,
            subject=subject,
        ).pack(),
        prev_page_callback=callback_data_factories.SubjectData(
            menu=callback_data_factories.NewsMenusEnum.subjects_list,
            back_menu=callback_data_factories.NewsMenusEnum.choose_subs_or_unsubs,
            page=current_page - 1,
            subscribed=subscribed,
            subject=subject,
        ).pack(),
        back_callback=callback_data_factories.SubjectData(
            menu=callback_data_factories.NewsMenusEnum.choose_subs_or_unsubs,
            back_menu=callback_data_factories.NewsMenusEnum.main_menu,
            subject=subject,
        ).pack(),
        end_callback=callback_data_factories.NewsMenuData(
            menu=callback_data_factories.NewsMenusEnum.end_menu,
        ).pack(),
    )


def get_periods_kb(
        periods: list[dict[str, Any]],
        get_period_news: callback_data_factories.NewsMenusEnum,
        back_menu: callback_data_factories.NewsMenuData,
) -> InlineKeyboardMarkup:
    """
    Клавиатура с выбором периода, за который выгружаются новости по клиенту

    :param periods: list[dict[text: str, days: int]]
    :param get_period_news: callback_data_factories.NewsMenusEnum обработчик выдачи новостей за период
    :param back_menu: callback_data_factories.NewsMenuData пункт меню, в который ведет кнопка Назад
    return:
    [ period.text ]
    ...
    [ Назад ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()

    for period in periods:
        keyboard.row(types.InlineKeyboardButton(
            text=period['text'],
            callback_data=callback_data_factories.NewsMenuData(
                menu=get_period_news,
                days_count=period['days'],
            ).pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=back_menu.pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.NewsMenuData(
            menu=callback_data_factories.NewsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()
