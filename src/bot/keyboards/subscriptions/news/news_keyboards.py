"""Клавиатуры по подпискам на новости"""
from typing import Type

import pandas as pd
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from constants.subscriptions import const
from keyboards.base import get_pagination_kb
from keyboards.subscriptions import callbacks, constructors


class BaseKeyboard:
    """Базовая клавиатура по подпискам на новости"""

    def __init__(
            self,
            callbacks,
            watch_subject_news_callback_factory: Type[CallbackData],
            can_write_subs: bool = True,
    ) -> None:
        self.callbacks = callbacks
        self.can_write_subs = can_write_subs
        self.watch_subject_news_callback_factory = watch_subject_news_callback_factory

    def get_prepare_subs_delete_all_kb(self) -> InlineKeyboardMarkup:
        """
        Формирует Inline клавиатуру вида:

        [ Да ][ Нет ]
        [   назад   ]
        """
        return constructors.get_approve_action_kb(
            self.callbacks.DeleteAllSubs().pack(),
            callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.delete_all_subscriptions).pack(),
            callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.delete_all_subscriptions).pack(),
        )

    def get_back_to_subscriptions_menu_kb(self) -> InlineKeyboardMarkup:
        """
        Формирует Inline клавиатуру вида:

        [   назад в меню   ]
        """
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(
            text=constants.BACK_BUTTON_TXT,
            callback_data=callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.delete_all_subscriptions).pack(),
        ))
        return keyboard.as_markup()

    def get_subscriptions_menu_kb(self) -> InlineKeyboardMarkup:
        """
        Формирует Inline клавиатуру вида:

        [ Просмотреть подписки ]
        [ Добавить новые подписки  ]
        [ Удалить все подписки ]
        """
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(
            text='Просмотреть подписки',
            callback_data=self.callbacks.GetUserSubs().pack(),
        ))
        keyboard.row(types.InlineKeyboardButton(
            text='Добавить новые подписки',
            callback_data=self.callbacks.ChangeUserSubs().pack(),
        ))
        keyboard.row(types.InlineKeyboardButton(
            text='Удалить подписки',
            callback_data=self.callbacks.DeleteUserSub().pack(),
        ))
        keyboard.row(types.InlineKeyboardButton(
            text='Удалить все подписки',
            callback_data=self.callbacks.PrepareDeleteAllSubs().pack(),
        ))
        keyboard.row(types.InlineKeyboardButton(
            text=constants.BACK_BUTTON_TXT,
            callback_data=const.SUBS_MENU,
        ))
        keyboard.row(types.InlineKeyboardButton(
            text=constants.END_BUTTON_TXT,
            callback_data=const.END_WRITE_SUBS,
        ))
        return keyboard.as_markup()

    def change_subs_menu(self) -> InlineKeyboardMarkup:
        """Меню изменение подписок"""
        keyboard = InlineKeyboardBuilder()
        if self.can_write_subs:
            keyboard.row(types.InlineKeyboardButton(
                text='Напишу сам/Справочник по подпискам',
                callback_data=self.callbacks.WriteSubs().pack(),
            ))
        keyboard.row(types.InlineKeyboardButton(
            text='Выберу из меню',
            callback_data=self.callbacks.SelectSubs().pack(),
        ))
        keyboard.row(types.InlineKeyboardButton(
            text=constants.BACK_BUTTON_TXT,
            callback_data=callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.change_subscriptions).pack(),
        ))
        keyboard.row(types.InlineKeyboardButton(
            text=constants.END_BUTTON_TXT,
            callback_data=const.END_WRITE_SUBS,
        ))
        return keyboard.as_markup()

    def show_industry_kb(self) -> InlineKeyboardMarkup:
        """Клавиатура по отрасли"""
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(
            text='Показать готовые подборки',
            callback_data=self.callbacks.ShowIndustry().pack(),
        ))
        keyboard.row(types.InlineKeyboardButton(
            text=constants.BACK_BUTTON_TXT,
            callback_data=self.callbacks.ChangeUserSubs().pack(),
        ))
        keyboard.row(types.InlineKeyboardButton(
            text=constants.END_BUTTON_TXT,
            callback_data=const.END_WRITE_SUBS,
        ))
        return keyboard.as_markup()

    def get_delete_user_subscription_kb(
            self,
            page_data: pd.DataFrame,
            current_page: int,
            max_pages: int,
    ) -> InlineKeyboardMarkup:
        """
        Формирует Inline клавиатуру вида:

        [ item 1 ][x]
        ...
        [ item N ][x]
        [<-][ Назад ][->]
        [ Завершить ]
        :param page_data: DataFrame[id, name]
        :param current_page: текущая страница меню, которую надо отобразить
        :param max_pages: всего страниц (для блокировки кнопок <- и ->, если достигли начала или конца)
        """
        page_data['action'] = constants.DELETE_CROSS
        page_data['action_callback'] = page_data['id'].apply(
            lambda x: self.callbacks.DeleteUserSub(page=current_page, subject_id=x).pack()
        )
        page_data['item_callback'] = 'None'
        return get_pagination_kb(
            page_data,
            current_page,
            max_pages,
            next_page_callback=self.callbacks.DeleteUserSub(page=current_page + 1).pack(),
            prev_page_callback=self.callbacks.DeleteUserSub(page=current_page - 1).pack(),
            back_callback=callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.delete_subscriptions).pack(),
            end_callback=const.END_WRITE_SUBS,
            reverse=True,
        )

    def get_watch_user_subscription_kb(
            self,
            page_data: pd.DataFrame,
            current_page: int,
            max_pages: int,
    ) -> InlineKeyboardMarkup:
        """
        Формирует Inline клавиатуру вида:

        [ item 1 ]
        ...
        [ item N ]
        [<-][ Назад ][->]
        [ Завершить ]
        :param page_data: DataFrame[id, name]
        :param current_page: текущая страница меню, которую надо отобразить
        :param max_pages: всего страниц (для блокировки кнопок <- и ->, если достигли начала или конца)
        """
        page_data['item_callback'] = page_data['id'].apply(
            lambda x: self.watch_subject_news_callback_factory(subject_id=x).pack()
        )
        return get_pagination_kb(
            page_data,
            current_page,
            max_pages,
            next_page_callback=self.callbacks.GetUserSubs(page=current_page + 1).pack(),
            prev_page_callback=self.callbacks.GetUserSubs(page=current_page - 1).pack(),
            back_callback=callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.my_subscriptions).pack(),
            end_callback=const.END_WRITE_SUBS,
        )

    def get_subjects_kb(self, page_data: pd.DataFrame, current_page: int, max_pages: int) -> InlineKeyboardMarkup:
        """
        Формирует Inline клавиатуру вида:

        [][ item 1 ]
        ...
        [][ item N ]
        [<-][ Назад ][->]
        [ Завершить ]
        :param page_data: DataFrame[id, name, is_subscribed]
        :param current_page: текущая страница меню, которую надо отобразить
        :param max_pages: всего страниц (для блокировки кнопок <- и ->, если достигли начала или конца)
        """
        page_data['action'] = page_data['is_subscribed'].apply(
            lambda x: constants.SELECTED if x else constants.UNSELECTED
        )
        page_data['action_callback'] = page_data.apply(
            lambda x: self.callbacks.SelectSubs(
                page=current_page, subject_id=x['id'], need_add=not x['is_subscribed']
            ).pack(),
            axis=1,
        )
        page_data['item_callback'] = 'None'
        return get_pagination_kb(
            page_data,
            current_page,
            max_pages,
            next_page_callback=self.callbacks.SelectSubs(page=current_page + 1).pack(),
            prev_page_callback=self.callbacks.SelectSubs(page=current_page - 1).pack(),
            back_callback=self.callbacks.ChangeUserSubs().pack(),
            end_callback=const.END_WRITE_SUBS,
        )
