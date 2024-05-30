"""
Модуль для формирования клавиатур для меню Новости.

Главное меню.
Меню выбора тг каналов.
Меню выбора тг разделов.
Меню выбора клиентов и сырья.
Меню выбора периода получения новостей.
"""
from typing import Any

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

    :param telegram_groups: Список тг групп
    """
    keyboard = InlineKeyboardBuilder()

    for telegram_group in telegram_groups:
        keyboard.row(types.InlineKeyboardButton(
            text=telegram_group.name,
            callback_data=callback_data_factories.TelegramGroupData(
                menu=callback_data_factories.NewsMenusEnum.choose_telegram_subjects,
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


def get_sections_menu_kb(
        telegram_sections: list[models.TelegramSection],
        group_id: int,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ section.name ]
    [ ... ]
    [ section.name ]
    [ Назад ]
    [ Завершить ]

    :param telegram_sections:   список разделов в группе (bot_telegram_section)
    :param group_id:            bot_telegram_group.id
    """
    keyboard = InlineKeyboardBuilder()

    for section in telegram_sections:
        keyboard.row(types.InlineKeyboardButton(
            text=section.name,
            callback_data=callback_data_factories.TelegramGroupData(
                menu=callback_data_factories.NewsMenusEnum.choose_source_group,
                telegram_group_id=group_id,
                telegram_section_id=section.id,
                back_menu=callback_data_factories.NewsMenusEnum.choose_telegram_subjects,
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


def get_select_telegram_channels_kb(
        telegram_channels: pd.DataFrame,
        callback_data: callback_data_factories.TelegramGroupData,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [✅/🟩][ telegram_channel['name'] ]
    [✅/🟩][ ... ]
    [✅/🟩][ telegram_channel['name'] ]
    [ Получить новости ]
    [ Назад ]
    [ Завершить ]

    :param telegram_channels:   Список телеграмм каналов, на которые можно подписаться (telegram_channel)
                              DataFrame[id, name, is_subscribed]
    :param callback_data:       Данные о текущем меню
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in telegram_channels.iterrows():
        add_del_call = callback_data_factories.TelegramGroupData(
            menu=callback_data.menu,
            subject_ids=callback_data.subject_ids,
            telegram_group_id=callback_data.telegram_group_id,
            telegram_section_id=callback_data.telegram_section_id,
            telegram_channel_id=item['id'],
            back_menu=callback_data.back_menu,
        )

        mark = constants.SELECTED if item['is_subscribed'] else constants.UNSELECTED
        keyboard.row(types.InlineKeyboardButton(text=mark, callback_data=add_del_call.pack()))
        keyboard.add(types.InlineKeyboardButton(text=item['name'], callback_data=add_del_call.pack()))

    keyboard.row(types.InlineKeyboardButton(
        text='Получить новости',
        callback_data=callback_data_factories.TelegramGroupData(
            menu=callback_data_factories.NewsMenusEnum.choose_period_for_telegram,
            subject_ids=callback_data.subject_ids,
            telegram_group_id=callback_data.telegram_group_id,
            telegram_section_id=callback_data.telegram_section_id,
            back_menu=callback_data.menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_data_factories.TelegramGroupData(
            menu=callback_data.back_menu,
            telegram_group_id=callback_data.telegram_group_id,
            telegram_section_id=callback_data.telegram_section_id,
            back_menu=callback_data.back_menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.NewsMenuData(
            menu=callback_data_factories.NewsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_choose_source_kb(
        callback_data: callback_data_factories.TelegramGroupData,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Телеграм каналы ]
    [ Внешние источники ]
    [ Назад ]
    [ Завершить ]

    :param callback_data:       Данные о текущем меню
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Телеграм каналы',
        callback_data=callback_data_factories.TelegramGroupData(
            menu=callback_data_factories.NewsMenusEnum.telegram_channels_by_section,
            telegram_group_id=callback_data.telegram_group_id,
            telegram_section_id=callback_data.telegram_section_id,
            is_external=False,
            back_menu=callback_data.back_menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Внешние источники',
        callback_data=callback_data_factories.TelegramGroupData(
            menu=callback_data_factories.NewsMenusEnum.choose_period_for_telegram,
            telegram_group_id=callback_data.telegram_group_id,
            telegram_section_id=callback_data.telegram_section_id,
            is_external=True,
            back_menu=callback_data.back_menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_data_factories.TelegramGroupData(
            menu=callback_data.back_menu,
            telegram_group_id=callback_data.telegram_group_id,
            telegram_section_id=callback_data.telegram_section_id,
            back_menu=callback_data.back_menu,
        ).pack(),
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
    Формирует клавиатуру вида:

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
        subject_interface: callback_data_factories.SubjectsInterfaces,
        selected_ids: str,
        back_menu: callback_data_factories.NewsMenuData,
) -> InlineKeyboardMarkup:
    """
    Клавиатура с выбором периода, за который выгружаются новости по клиенту

    :param periods:             list[dict[text: str, days: int]]
    :param subject_interface:   SubjectInterface обработчик выдачи новостей за период
    :param selected_ids:        id выбранных субъектов, по которым надо получить новости
    :param back_menu:           callback_data_factories.NewsMenuData пункт меню, в который ведет кнопка Назад
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
                menu=callback_data_factories.NewsMenusEnum.news_by_period,
                days_count=period['days'],
                interface=subject_interface,
                subject_ids=selected_ids,
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
