from typing import Any, Optional

import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from handlers.clients import callback_data_factories
from keyboards.base import get_pagination_kb


def get_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Выбрать клиента из списка подписок ]
    [ Выбрать другого клиента ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Выбрать клиента из моего списка подписок',
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.clients_list,
            subscribed=True,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Выбрать другого клиента',
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.clients_list,
            subscribed=False,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_clients_list_kb(
        page_data: pd.DataFrame,
        current_page: int,
        max_pages: int,
        subscribed: bool,
) -> InlineKeyboardMarkup:
    """
    [ item 1 ]
    ...
    [ item N ]
    [<-][ Назад ][->]
    [ Завершить ]
    :param page_data: DataFrame[id, name]
    :param current_page: текущая страница меню, которую надо отобразить
    :param max_pages: всего страниц (для блокировки кнопок <- и ->, если достигли начала или конца)
    :param subscribed: флаг, что выбран клиент из подписок или нет
    """
    page_data['name'] = page_data['name'].str.capitalize()
    page_data['item_callback'] = page_data['id'].apply(
        lambda x: callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.client_menu,
            client_id=x,
            page=current_page,
            subscribed=subscribed,
        ).pack()
    )
    return get_pagination_kb(
        page_data,
        current_page,
        max_pages,
        next_page_callback=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.clients_list,
            page=current_page + 1,
            subscribed=subscribed,
        ).pack(),
        prev_page_callback=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.clients_list,
            page=current_page - 1,
            subscribed=subscribed,
        ).pack(),
        back_callback=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.main_menu,
        ).pack(),
        end_callback=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.end_menu,
        ).pack(),
    )


def get_client_menu_kb(
        client_id: int,
        current_page: int,
        subscribed: bool = False,
        research_type_id: Optional[int] = None,
        with_back_button: bool = True,
) -> InlineKeyboardMarkup:
    """
    [ Новости ]
    [ Аналитика публичных рынков ] [если публичный]
    [ Отраслевая аналитика ]
    [ Продуктовые предложения ]
    [ Цифровая справка ]
    [ Сформировать материалы для встречи ]
    [ Call-reports ]
    Optional{ [ Назад ] }
    [ Завершить ]
    :param client_id: client.id
    :param current_page: ClientsMenuData.page
    :param subscribed: ClientsMenuData.subscribed
    :param research_type_id: research_type.id | None
    :param with_back_button: нужна ли кнопка назад
    :return: клавиатура
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.row(types.InlineKeyboardButton(
        text='Новости',
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.client_news_menu,
            client_id=client_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))

    if research_type_id:
        keyboard.row(types.InlineKeyboardButton(
            text='Аналитика публичных рынков',
            callback_data=callback_data_factories.ClientsMenuData(
                menu=callback_data_factories.ClientsMenusEnum.analytic_indicators,
                client_id=client_id,
                research_type_id=research_type_id,
                page=current_page,
                subscribed=subscribed,
            ).pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text='Отраслевая аналитика',
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.industry_analytics,
            client_id=client_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Продуктовые предложения',
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.products,
            client_id=client_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Цифровая справка',
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.inavigator,
            client_id=client_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))
    # keyboard.row(types.InlineKeyboardButton(
    #     text='Сформировать материалы для встречи',
    #     callback_data=callback_data_factories.ClientsMenuData(
    #         menu=callback_data_factories.ClientsMenusEnum.meetings_data,
    #         client_id=client_id,
    #         page=current_page,
    #         subscribed=subscribed,
    #     ).pack(),
    # ))
    # keyboard.row(types.InlineKeyboardButton(
    #     text='Call reports',
    #     callback_data=callback_data_factories.ClientsMenuData(
    #         menu=callback_data_factories.ClientsMenusEnum.call_reports,
    #         client_id=client_id,
    #         page=current_page,
    #         subscribed=subscribed,
    #     ).pack(),
    # ))
    if with_back_button:
        keyboard.row(types.InlineKeyboardButton(
            text=constants.BACK_BUTTON_TXT,
            callback_data=callback_data_factories.ClientsMenuData(
                menu=callback_data_factories.ClientsMenusEnum.clients_list,
                page=current_page,
                subscribed=subscribed,
            ).pack(),
        ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_news_menu_kb(
        client_id: int,
        current_page: int,
        subscribed: bool,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Аналитика sell-side ]
    [ Отраслевая аналитика ]
    [ Завершить ]
    :param client_id: client.id
    :param current_page: ClientsMenuData.page
    :param subscribed: ClientsMenuData.subscribed
    """
    keyboard = InlineKeyboardBuilder()
    # keyboard.row(types.InlineKeyboardButton(
    #     text='Топ новости',
    #     callback_data=callback_data_factories.ClientsMenuData(
    #         menu=callback_data_factories.ClientsMenusEnum.top_news,
    #         client_id=client_id,
    #         page=current_page,
    #         subscribed=subscribed,
    #     ).pack(),
    # ))
    keyboard.row(types.InlineKeyboardButton(
        text='Получить новости за период',
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.select_period,
            client_id=client_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.client_menu,
            client_id=client_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_periods_kb(
        client_id: int,
        current_page: int,
        subscribed: bool,
        research_type_id: int,
        periods: list[dict[str, Any]],
        select_period_menu: callback_data_factories.ClientsMenusEnum,
        back_menu: callback_data_factories.ClientsMenusEnum,
) -> InlineKeyboardMarkup:
    """
    Клавиатура с выбором периода, за который выгружаются новости по клиенту

    :param client_id: client.id
    :param current_page: ClientsMenuData.page
    :param subscribed: ClientsMenuData.subscribed
    :param research_type_id: ClientsMenuData.research_type_id
    :param periods: list[dict[text: str, days: int]]
    :param select_period_menu: callback_data_factories.ClientsMenusEnum пункт меню, в который ведет выбор периода
    :param back_menu: callback_data_factories.ClientsMenusEnum пункт меню, в который ведет кнопка Назад
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
            callback_data=callback_data_factories.ClientsMenuData(
                menu=select_period_menu,
                client_id=client_id,
                research_type_id=research_type_id,
                days_count=period['days'],
                page=current_page,
                subscribed=subscribed,
            ).pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=back_menu,
            client_id=client_id,
            research_type_id=research_type_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def get_products_menu_kb(
        client_id: int,
        current_page: int,
        subscribed: bool,
) -> InlineKeyboardMarkup:
    """
    [ hot offers ]
    [ Назад ]
    [ Завершить ]
    :param client_id: client.id
    :param current_page: ClientsMenuData.page
    :param subscribed: ClientsMenuData.subscribed
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.row(types.InlineKeyboardButton(
        text='Hot offers',
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.hot_offers,
            client_id=client_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.client_menu,
            client_id=client_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()


def client_analytical_indicators_kb(
        client_id: int,
        current_page: int,
        subscribed: bool,
        research_type_id: int,
) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Аналитические обзоры ]
    [ P&L модель ]
    [ Модель баланса ]
    [ Модель CF ]
    [ Коэффициенты ]
    [  назад  ]
    [   Завершить   ]

    :param client_id: client.id
    :param current_page: ClientsMenuData.page
    :param subscribed: ClientsMenuData.subscribed
    :param research_type_id: ClientsMenuData.research_type_id
    """
    keyboard = InlineKeyboardBuilder()

    buttons = [
        {
            'name': 'Аналитические обзоры',
            'callback_data': callback_data_factories.ClientsMenuData(
                menu=callback_data_factories.ClientsMenusEnum.analytic_reports,
                client_id=client_id,
                research_type_id=research_type_id,
                page=current_page,
                subscribed=subscribed,
            ).pack(),
        },
        # {
        #     'name': 'P&L модель',
        #     'callback_data': callback_data_factories.ClientsMenuData(
        #         menu=callback_data_factories.ClientsMenusEnum.not_implemented,
        #     ).pack(),
        # },
        # {
        #     'name': 'Модель баланса',
        #     'callback_data': callback_data_factories.ClientsMenuData(
        #         menu=callback_data_factories.ClientsMenusEnum.not_implemented,
        #     ).pack(),
        # },
        # {
        #     'name': 'Модель CF',
        #     'callback_data': callback_data_factories.ClientsMenuData(
        #         menu=callback_data_factories.ClientsMenusEnum.not_implemented,
        #     ).pack(),
        # },
        # {
        #     'name': 'Коэффициенты',
        #     'callback_data': callback_data_factories.ClientsMenuData(
        #         menu=callback_data_factories.ClientsMenusEnum.not_implemented,
        #     ).pack(),
        # },
    ]

    for item in buttons:
        keyboard.row(types.InlineKeyboardButton(
            text=item['name'],
            callback_data=item['callback_data'],
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.client_menu,
            client_id=client_id,
            research_type_id=research_type_id,
            page=current_page,
            subscribed=subscribed,
        ).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.ClientsMenuData(
            menu=callback_data_factories.ClientsMenusEnum.end_menu,
        ).pack(),
    ))
    return keyboard.as_markup()
