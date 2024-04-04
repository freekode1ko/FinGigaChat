from typing import Any

import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from constants import subscriptions as callback_prefixes
from keyboards.subscriptions import constructors
from keyboards.subscriptions.research import callbacks
from utils.base import wrap_callback_data, unwrap_callback_data


def get_research_subscriptions_main_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Просмотреть подписки ]
    [ Изменить подписки    ]
    [ Удалить все подписки ]
    [      Завершить       ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Просмотреть подписки',
        callback_data=callbacks.GetUserCIBResearchSubs(page=0).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Изменить подписки',
        callback_data=callbacks.GetCIBGroups().pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Удалить все подписки',
        callback_data=callback_prefixes.CIB_RESEARCH_SUBS_APPROVE_DELETE_ALL,
    ))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.SUBS_MENU))
    keyboard.row(types.InlineKeyboardButton(text='Завершить',
                                            callback_data=callback_prefixes.CIB_RESEARCH_END_WRITE_SUBS))
    return keyboard.as_markup()


def get_user_research_subs_kb(page_data: pd.DataFrame, page: int, max_pages: int) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ domain/research ][❌]
    [ domain/research ][❌]
    [ domain/research ][❌]
    [ <- ][  назад  ][ -> ]

    :param page_data: Данные о подписках на отчеты из CIB Research на данной странице
    :param page: Номер страницы. Нужен для формирования callback_data
    :param max_pages: Всего страниц
    """
    keyboard = InlineKeyboardBuilder()

    for index, sub in page_data.iterrows():
        more_info_call = callbacks.GetCIBResearchTypeMoreInfo(
            research_id=sub['id'],
            is_subscribed=True,
            back=wrap_callback_data(callbacks.GetUserCIBResearchSubs(page=page).pack()),
        ).pack()
        delete_call = callbacks.GetUserCIBResearchSubs(page=page, del_sub_id=sub['id']).pack()
        keyboard.row(types.InlineKeyboardButton(text=sub['name'], callback_data=more_info_call))
        keyboard.add(types.InlineKeyboardButton(text=constants.DELETE_CROSS, callback_data=delete_call))

    if page != 0:
        keyboard.row(types.InlineKeyboardButton(
            text=constants.PREV_PAGE,
            callback_data=callbacks.GetUserCIBResearchSubs(page=page - 1).pack(),
        ))
    else:
        keyboard.row(types.InlineKeyboardButton(text=constants.STOP, callback_data='constants.STOP'))

    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU))

    if page < max_pages - 1:
        keyboard.add(types.InlineKeyboardButton(
            text=constants.NEXT_PAGE,
            callback_data=callbacks.GetUserCIBResearchSubs(page=page + 1).pack(),
        ))
    else:
        keyboard.add(types.InlineKeyboardButton(text=constants.STOP, callback_data='constants.STOP'))

    keyboard.row(types.InlineKeyboardButton(text='Завершить',
                                            callback_data=callback_prefixes.CIB_RESEARCH_END_WRITE_SUBS))
    return keyboard.as_markup()


def get_research_type_info_kb(cib_research_type_id: int, is_subscribed: bool, back: str) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Подписаться/Удалить из подписок ]
    [   назад   ]

    :param cib_research_type_id: cib_research_type_id
    :param is_subscribed: флаг, подписан ли пользователь на этот канал
    :param back: упакованные данные для callback_data
    """
    keyboard = InlineKeyboardBuilder()

    add_del_text = 'Подписаться' if not is_subscribed else 'Удалить из подписок'

    action_call = callbacks.CIBResearchSubAction(
        research_id=cib_research_type_id,
        need_add=not is_subscribed,
        back=back
    ).pack()
    keyboard.row(types.InlineKeyboardButton(text=add_del_text, callback_data=action_call))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=unwrap_callback_data(back)))
    return keyboard.as_markup()


def get_research_groups_menu_kb(group_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]

    :param group_df: DataFrame[id, name] инфа о группах CIB Research
    """
    keyboard = InlineKeyboardBuilder()

    for index, item in group_df.iterrows():
        get_group_sections_callback = callbacks.GetCIBGroupSections(
            group_id=item['id'],
        )

        keyboard.row(types.InlineKeyboardButton(
            text=item['name'].capitalize(),
            callback_data=get_group_sections_callback.pack()),
        )

    # keyboard.row(types.InlineKeyboardButton(
    #     text='Подписаться на все',
    #     callback_data=callbacks.UpdateSubOnCIBSection().pack()
    # ))
    keyboard.row(types.InlineKeyboardButton(
        text='Назад',
        callback_data=callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Завершить',
        callback_data=callback_prefixes.CIB_RESEARCH_END_WRITE_SUBS
    ))
    return keyboard.as_markup()


def get_research_sections_by_group_menu_kb(
        group_info: dict[str, Any],
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
        if item['dropdown_flag']:
            button_txt = item['name'].capitalize()
            section_callback = callbacks.GetCIBSectionResearches(
                group_id=group_info['id'],
                section_id=item['id'],
            )
        else:
            mark = constants.SELECTED if item['is_subscribed'] else constants.UNSELECTED
            button_txt = f'{mark} {item["name"].capitalize()}'
            section_callback = callbacks.GetCIBGroupSections(
                group_id=group_info['id'],
                section_id=item['id'],
                need_add=int(not item['is_subscribed']),
            )

        keyboard.row(types.InlineKeyboardButton(
            text=button_txt,
            callback_data=section_callback.pack()),
        )

    # keyboard.row(types.InlineKeyboardButton(
    #     text='Подписаться на все',
    #     callback_data=callbacks.UpdateSubOnCIBSection().pack()
    # ))
    keyboard.row(types.InlineKeyboardButton(
        text='Назад',
        callback_data=callbacks.GetCIBGroups().pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Завершить',
        callback_data=callback_prefixes.CIB_RESEARCH_END_WRITE_SUBS,
    ))
    return keyboard.as_markup()


def get_research_types_by_section_menu_kb(
        group_id: int,
        section_id: int,
        research_types_df: pd.DataFrame,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [][ отчет 1 ]
    ...
    [][ отчет n ]
    [   назад   ]

    :param group_id: id группы CIB Research
    :param section_id: id раздела CIB Research
    :param research_types_df: DataFrame[id, name, is_signed] инфа о подборке подписок
    """
    keyboard = InlineKeyboardBuilder()

    for index, item in research_types_df.iterrows():
        add_del_call = callbacks.GetCIBSectionResearches(
            group_id=group_id,
            section_id=section_id,
            research_id=item['id'],
            need_add=int(not item['is_subscribed']),
        )
        mark = constants.SELECTED if item['is_subscribed'] else constants.UNSELECTED
        button_txt = f'{mark} {item["name"].capitalize()}'
        keyboard.row(types.InlineKeyboardButton(text=button_txt, callback_data=add_del_call.pack()))

    # keyboard.row(types.InlineKeyboardButton(
    #     text='Подписаться на все',
    #     callback_data=callbacks.UpdateSubOnCIBSection(domain_id=domain_id, is_domain_page=False).pack(),
    # ))
    keyboard.row(types.InlineKeyboardButton(text='Назад',
                                            callback_data=callbacks.GetCIBGroupSections(group_id=group_id).pack()))
    keyboard.row(types.InlineKeyboardButton(text='Завершить',
                                            callback_data=callback_prefixes.CIB_RESEARCH_END_WRITE_SUBS))
    return keyboard.as_markup()


def get_research_subs_approve_delete_all_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Да ][ Нет ]
    [   назад   ]
    """
    return constructors.get_approve_action_kb(
        callback_prefixes.CIB_RESEARCH_SUBS_DELETE_ALL,
        callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU,
        callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU,
    )


def get_back_to_research_subs_main_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [   назад в меню   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.GET_CIB_RESEARCH_SUBS_MENU))
    return keyboard.as_markup()
