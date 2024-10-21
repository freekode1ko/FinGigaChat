"""Клавиатуры для подписок"""
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from constants.subscriptions import const
from constants.subscriptions import research
from keyboards.subscriptions import callbacks
from keyboards.subscriptions.news.client import callbacks as client_callback_factory
from keyboards.subscriptions.news.commodity import callbacks as commodity_callback_factory
from keyboards.subscriptions.news.industry import callbacks as industry_callback_factory
from keyboards.subscriptions.news.telegram import callbacks as telegram_callback_factory
from keyboards.subscriptions.research import callbacks as research_callback_factory


def get_approve_action_kb(yes_callback: str, no_callback: str, back_callback: str) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Да ][ Нет ]
    [   назад   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data=yes_callback))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data=no_callback))
    keyboard.row(types.InlineKeyboardButton(text=constants.BACK_BUTTON_TXT, callback_data=back_callback))
    return keyboard.as_markup()


def get_main_menu_kb() -> InlineKeyboardMarkup:
    """
    Главное меню подписок

    :return: keyboard для главного меню подписок
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Изменить подписки',
        callback_data=callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.change_subscriptions).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Посмотреть подписки',
        callback_data=callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.my_subscriptions).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Посмотреть все мои подписки',
        callback_data=const.SHOW_ALL_SUBS,
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Удалить все подписки',
        callback_data=callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.delete_all_subscriptions).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(text=constants.END_BUTTON_TXT, callback_data=const.END_WRITE_SUBS))
    return keyboard.as_markup()


def get_subscriptions_menu_kb(menu_type: callbacks.SubsMenusEnum) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Подписки на клиентов ]
    [ Подписки на сырьевые товары ]
    [ Подписки на отрасли ]
    [ Подписки на телеграм-каналы ]
    [ Подписки на аналитические отчеты ]
    [ Завершить  ]
    """
    match menu_type:
        case callbacks.SubsMenusEnum.my_subscriptions:
            buttons = {
                'Подписки на новости по компаниям': client_callback_factory.GetUserSubs().pack(),
                'Подписки на новости по сырью': commodity_callback_factory.GetUserSubs().pack(),
                'Подписки на отраслевые новости': industry_callback_factory.GetUserSubs().pack(),
                'Подписки на новости из телеграм-каналов': telegram_callback_factory.TelegramSubsMenuData(
                    menu=telegram_callback_factory.TelegramSubsMenusEnum.main_menu,
                    action=callbacks.SubsMenusEnum.my_subscriptions,
                ).pack(),
                'Подписки на аналитику': research_callback_factory.GetUserCIBResearchSubs(
                    action=callbacks.SubsMenusEnum.my_subscriptions,
                ).pack(),
            }
        case callbacks.SubsMenusEnum.change_subscriptions:
            buttons = {
                'Подписки на новости по компаниям': client_callback_factory.ChangeUserSubs().pack(),
                'Подписки на новости по сырью': commodity_callback_factory.ChangeUserSubs().pack(),
                'Подписки на отраслевые новости': industry_callback_factory.SelectSubs().pack(),
                'Подписки на новости из телеграм-каналов': telegram_callback_factory.TelegramSubsMenuData(
                    menu=telegram_callback_factory.TelegramSubsMenusEnum.main_menu,
                    action=callbacks.SubsMenusEnum.change_subscriptions,
                ).pack(),
                'Подписки на аналитику': research_callback_factory.GetCIBGroups().pack(),
            }
        case callbacks.SubsMenusEnum.delete_subscriptions:
            buttons = {
                'Подписки на новости по компаниям': client_callback_factory.DeleteUserSub().pack(),
                'Подписки на новости по сырью': commodity_callback_factory.DeleteUserSub().pack(),
                'Подписки на отраслевые новости': industry_callback_factory.DeleteUserSub().pack(),
                'Подписки на новости из телеграм-каналов': telegram_callback_factory.TelegramSubsMenuData(
                    menu=telegram_callback_factory.TelegramSubsMenusEnum.main_menu,
                    action=callbacks.SubsMenusEnum.delete_subscriptions,
                ).pack(),
                'Подписки на аналитику': research_callback_factory.GetUserCIBResearchSubs(
                    action=callbacks.SubsMenusEnum.delete_subscriptions,
                ).pack(),
            }
        case callbacks.SubsMenusEnum.delete_all_subscriptions:
            buttons = {
                'Подписки на новости по компаниям': client_callback_factory.PrepareDeleteAllSubs().pack(),
                'Подписки на новости по сырью': commodity_callback_factory.PrepareDeleteAllSubs().pack(),
                'Подписки на отраслевые новости': industry_callback_factory.PrepareDeleteAllSubs().pack(),
                'Подписки на новости из телеграм-каналов': telegram_callback_factory.TelegramSubsMenuData(
                    menu=telegram_callback_factory.TelegramSubsMenusEnum.main_menu,
                    action=callbacks.SubsMenusEnum.delete_all_subscriptions,
                ).pack(),
                'Подписки на аналитику': research.CIB_RESEARCH_SUBS_APPROVE_DELETE_ALL,
            }
        case _:
            buttons = {}
    return __inner_get_subscriptions_menu_kb(buttons)


def __inner_get_subscriptions_menu_kb(buttons: dict[str, str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for button_text, button_callback in buttons.items():
        keyboard.row(types.InlineKeyboardButton(text=button_text, callback_data=button_callback))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callbacks.SubsMenuData(menu=callbacks.SubsMenusEnum.main_menu).pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(text=constants.END_BUTTON_TXT, callback_data=const.END_WRITE_SUBS))
    return keyboard.as_markup()
