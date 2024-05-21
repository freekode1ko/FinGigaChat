from aiogram.filters.callback_data import CallbackData

from constants.subscriptions.news import industry as callback_prefixes


class Menu(CallbackData, prefix=callback_prefixes.INDUSTRY_SUBS_MENU):
    """Меню управления подписками на отрасли"""
    pass


class GetUserSubs(CallbackData, prefix=callback_prefixes.GET_MY_SUBS):
    """Меню просмотра своих подписок на отрасли"""
    page: int = 0


class ChangeUserSubs(CallbackData, prefix=callback_prefixes.CHANGE_MY_SUBS):
    """Меню выбора вариантов добавления подписок"""
    pass


class DeleteUserSub(CallbackData, prefix=callback_prefixes.DELETE_MY_SUB):
    """Меню удаления подписок на отрасли. Если subject_id != 0, то удаляем подписку"""
    page: int = 0
    subject_id: int = 0


class PrepareDeleteAllSubs(CallbackData, prefix=callback_prefixes.PREPARE_DELETE_ALL_SUBS):
    """Меню удаления всех подписок на отрасли"""
    pass


class DeleteAllSubs(CallbackData, prefix=callback_prefixes.INDUSTRY_SUBS_DELETE_ALL_DONE):
    """Сообщение, что все подписки по отраслям удалены"""
    pass


class SelectSubs(CallbackData, prefix=callback_prefixes.SELECT_SUBS):
    """Меню добавления подписок на отрасли"""
    page: int = 0
    subject_id: int = 0
    need_add: bool = False


class WriteSubs(CallbackData, prefix=callback_prefixes.WRITE_SUBS):
    """Режим ручного ввода подписок"""
    pass


class ShowIndustry(CallbackData, prefix=callback_prefixes.SHOW_INDUSTRY_INDUSTRIES):
    """Готовые подборки"""
    pass


class WhatInThisIndustry(CallbackData, prefix=callback_prefixes.WHAT_IN_THIS_INDUSTRY):
    """Подборка по отрасли"""
    industry_id: int


class AddAllSubsByDomain(CallbackData, prefix=callback_prefixes.ADD_ALL_INDUSTRY_SUBS_BY_DOMAIN):
    """Добавление всех отраслей в области"""
    domain: str
