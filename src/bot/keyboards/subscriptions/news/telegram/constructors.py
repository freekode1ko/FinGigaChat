"""Клавиатуры по подпискам на каналы в телеграмме"""
import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from constants.subscriptions import const
from db import models
from keyboards.subscriptions import constructors
from keyboards.subscriptions.news.telegram import callbacks as callback_factory


def get_tg_info_kb(callback_data: callback_factory.TelegramSubsMenuData) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Подписаться/Удалить из подписок ]
    [   назад   ]

    :param callback_data: Содержит информацию о текущем меню
    """
    keyboard = InlineKeyboardBuilder()

    add_del_text = 'Подписаться' if not callback_data.is_subscribed else 'Удалить из подписок'

    action_call = callback_factory.TelegramSubsMenuData(
        menu=callback_factory.TelegramSubsMenusEnum.telegram_channel_info,
        group_id=callback_data.group_id,
        section_id=callback_data.section_id,
        telegram_id=callback_data.telegram_id,
        is_subscribed=not callback_data.is_subscribed,
        need_add=not callback_data.is_subscribed,
        back_menu=callback_data.back_menu,
    )

    back_call = callback_factory.TelegramSubsMenuData(
        menu=callback_data.back_menu,
        group_id=callback_data.group_id,
        section_id=callback_data.section_id,
        back_menu=callback_data.back_menu,
    )
    keyboard.row(types.InlineKeyboardButton(text=add_del_text, callback_data=action_call.pack()))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=back_call.pack(),
    ))
    return keyboard.as_markup()


def get_groups_kb(groups: list[models.TelegramGroup]) -> InlineKeyboardMarkup:
    """
    Формирует клавиатуру вида

    [ group.name ]
    [ ... ]
    [ group.name ]
    [ Back ]
    [ End ]
    :param groups: Список групп, выделенных среди тг каналов
    """
    keyboard = InlineKeyboardBuilder()

    for group in groups:
        callback_data = callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.group_main_menu,
            group_id=group.id,
        )

        keyboard.row(types.InlineKeyboardButton(
            text=group.name,
            callback_data=callback_data.pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=const.SUBS_MENU,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_group_main_menu_kb(group_id: int) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Просмотреть подписки ]
    [ Изменить подписки    ]
    [ Удалить все подписки ]
    [ Назад ]
    [ Завершить ]
    :param group_id: bot_telegram_group.id
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Просмотреть подписки',
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.my_subscriptions,
            group_id=group_id,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Изменить подписки',
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.change_subscriptions,
            group_id=group_id,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Удалить все подписки',
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.approve_delete_menu,
            group_id=group_id,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.main_menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_my_subscriptions_kb(page_data: pd.DataFrame, page: int, max_pages: int, group_id: int) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ telegram channel name ][❌]
    [ telegram channel name ][❌]
    [ telegram channel name ][❌]
    [ <- ][     назад     ][ -> ]

    :param page_data: Данные о тг подписках на данной странице [id, name]
    :param page: Номер страницы. Нужен для формирования callback_data
    :param max_pages: Всего страниц
    :param group_id: bot_telegram_group.id
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in page_data.iterrows():
        more_info_call = callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.telegram_channel_info,
            group_id=group_id,
            page=page,
            telegram_id=item['id'],
            is_subscribed=True,
            back_menu=callback_factory.TelegramSubsMenusEnum.my_subscriptions,
        )
        delete_call = callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.my_subscriptions,
            group_id=group_id,
            page=page,
            telegram_id=item['id'],
            is_subscribed=True,
        )
        keyboard.row(types.InlineKeyboardButton(text=item['name'], callback_data=more_info_call.pack()))
        keyboard.add(types.InlineKeyboardButton(text=constants.DELETE_CROSS, callback_data=delete_call.pack()))

    if page != 0:
        keyboard.row(types.InlineKeyboardButton(
            text=constants.PREV_PAGE,
            callback_data=callback_factory.TelegramSubsMenuData(
                menu=callback_factory.TelegramSubsMenusEnum.my_subscriptions,
                group_id=group_id,
                page=page - 1,
            ).pack(),
        ))
    else:
        keyboard.row(types.InlineKeyboardButton(text=constants.STOP, callback_data='constants.STOP'))

    keyboard.add(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.group_main_menu,
            group_id=group_id,
        ).pack(),
    ))

    if page < max_pages - 1:
        keyboard.add(types.InlineKeyboardButton(
            text=constants.NEXT_PAGE,
            callback_data=callback_factory.TelegramSubsMenuData(
                menu=callback_factory.TelegramSubsMenusEnum.my_subscriptions,
                group_id=group_id,
                page=page + 1,
            ).pack(),
        ))
    else:
        keyboard.add(types.InlineKeyboardButton(text=constants.STOP, callback_data='constants.STOP'))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.end_menu,
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
    :param telegram_sections: список разделов в группе (bot_telegram_section)
    :param group_id: bot_telegram_group.id
    """
    keyboard = InlineKeyboardBuilder()

    for section in telegram_sections:
        keyboard.row(types.InlineKeyboardButton(
            text=section.name,
            callback_data=callback_factory.TelegramSubsMenuData(
                menu=callback_factory.TelegramSubsMenusEnum.telegram_channels_by_section,
                group_id=group_id,
                section_id=section.id,
                back_menu=callback_factory.TelegramSubsMenusEnum.change_subscriptions,
            ).pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.group_main_menu,
            group_id=group_id,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_change_subscriptions_kb(
        telegram_channels: pd.DataFrame,
        callback_data: callback_factory.TelegramSubsMenuData,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [✅/🟩][ telegram_channel['name'] ]
    [✅/🟩][ ... ]
    [✅/🟩][ telegram_channel['name'] ]
    [ Назад ]
    [ Завершить ]
    :param telegram_channels: Список телеграмм каналов, на которые можно подписаться (telegram_channel)
                              DataFrame[id, name, is_subscribed]
    :param callback_data: Данные о текущем меню
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in telegram_channels.iterrows():
        add_del_call = callback_factory.TelegramSubsMenuData(
            menu=callback_data.menu,
            group_id=callback_data.group_id,
            section_id=callback_data.section_id,
            telegram_id=item['id'],
            is_subscribed=item['is_subscribed'],
            back_menu=callback_data.back_menu,
        )
        more_info_call = callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.telegram_channel_info,
            group_id=callback_data.group_id,
            section_id=callback_data.section_id,
            telegram_id=item['id'],
            is_subscribed=item['is_subscribed'],
            back_menu=callback_data.menu,
        )

        mark = constants.SELECTED if item['is_subscribed'] else constants.UNSELECTED
        keyboard.row(types.InlineKeyboardButton(text=mark, callback_data=add_del_call.pack()))
        keyboard.add(types.InlineKeyboardButton(text=item['name'], callback_data=more_info_call.pack()))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_data.back_menu,
            group_id=callback_data.group_id,
            section_id=callback_data.section_id,
            back_menu=callback_data.back_menu,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_prepare_tg_subs_delete_all_kb(group_id: int) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Да ][ Нет ]
    [   назад   ]
    :param group_id: bot_telegram_group.id
    """
    delete_subs_callback_data = callback_factory.TelegramSubsMenuData(
        menu=callback_factory.TelegramSubsMenusEnum.delete_subscriptions_by_group,
        group_id=group_id,
    ).pack()
    back_callback_data = callback_factory.TelegramSubsMenuData(
        menu=callback_factory.TelegramSubsMenusEnum.group_main_menu,
        group_id=group_id,
    ).pack()
    return constructors.get_approve_action_kb(
        delete_subs_callback_data,
        back_callback_data,
        back_callback_data,
    )


def get_back_to_tg_subs_menu_kb(group_id: int) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [   назад в меню   ]
    :param group_id: bot_telegram_group.id
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_factory.TelegramSubsMenuData(
            menu=callback_factory.TelegramSubsMenusEnum.group_main_menu,
            group_id=group_id,
        ).pack(),
    ))
    return keyboard.as_markup()
