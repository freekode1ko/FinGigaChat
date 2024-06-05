"""CallbackData по подпискам на новости по сырьевым товарам"""
from aiogram.filters.callback_data import CallbackData

from constants.subscriptions.news import commodity as callback_prefixes


class Menu(CallbackData, prefix=callback_prefixes.COMMODITY_SUBS_MENU):
    """Меню управления подписками на сырьевые товары"""

    pass


class GetUserSubs(CallbackData, prefix=callback_prefixes.GET_MY_SUBS):
    """Меню просмотра своих подписок на сырьевые товары"""

    page: int = 0


class ChangeUserSubs(CallbackData, prefix=callback_prefixes.CHANGE_MY_SUBS):
    """Меню выбора вариантов добавления подписок"""

    pass


class DeleteUserSub(CallbackData, prefix=callback_prefixes.DELETE_MY_SUB):
    """Меню удаления подписок на сырьевые товары. Если subject_id != 0, то удаляем подписку"""

    page: int = 0
    subject_id: int = 0


class PrepareDeleteAllSubs(CallbackData, prefix=callback_prefixes.PREPARE_DELETE_ALL_SUBS):
    """Меню удаления всех подписок на сырьевые товары"""

    pass


class DeleteAllSubs(CallbackData, prefix=callback_prefixes.COMMODITY_SUBS_DELETE_ALL_DONE):
    """Сообщение, что все подписки по сырьевым товарам удалены"""

    pass


class SelectSubs(CallbackData, prefix=callback_prefixes.SELECT_SUBS):
    """Меню добавления подписок на сырьевые товары"""

    page: int = 0
    subject_id: int = 0
    need_add: bool = False


class WriteSubs(CallbackData, prefix=callback_prefixes.WRITE_SUBS):
    """Режим ручного ввода подписок"""

    pass


class ShowIndustry(CallbackData, prefix=callback_prefixes.SHOW_INDUSTRY_COMMODITIES):
    """Готовые подборки"""

    pass


class WhatInThisIndustry(CallbackData, prefix=callback_prefixes.WHAT_IN_THIS_INDUSTRY):
    """Подборка по отрасли"""

    industry_id: int


class AddAllSubsByDomain(CallbackData, prefix=callback_prefixes.ADD_ALL_COMMODITY_SUBS_BY_DOMAIN):
    """Добавление всех товаров в области"""

    domain: str
