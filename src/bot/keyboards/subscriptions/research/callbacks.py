from aiogram.filters.callback_data import CallbackData

from constants import subscriptions as callback_prefixes


class GetUserCIBResearchSubs(CallbackData, prefix=callback_prefixes.USER_CIB_RESEARCH_SUBS):
    """
    Подписки пользователя на отчеты CIB
    Если delete_sub_id != 0, то удаление подписки
    """
    page: int = 0
    del_sub_id: int = 0


class GetCIBResearchTypeMoreInfo(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_INFO):
    """Доп. инфо по отчету, на который можно подписаться"""
    cib_type_id: int
    is_subscribed: bool = False
    back: str


class GetCIBDomains(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_DOMAINS_MENU):
    """Меню разделов"""
    pass


class UpdateSubOnCIBDomain(CallbackData, prefix=callback_prefixes.UPDATE_CIB_RESEARCH_DOMAIN_SUB):
    """
    Подписка/отписка на весь раздел domain_id, если domain_id != 0, иначе подписка на все разделы
    Отрисовка страницы меню с разделами, если is_domain_page, иначе отрисовка меню подписок на отчеты для раздела domain_id (domain_id != 0)
    """
    domain_id: int = 0
    is_domain_page: bool = True


class GetCIBDomainResearchTypes(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_DOMAIN_TYPES_MENU):
    """
    Меню отчетов для раздела domain_id
    Если
    """
    domain_id: int
    cib_type_id: int = 0
    need_add: int = 0


class CIBResearchSubAction(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_SUB_ACTION):
    """Подписка/отписка на отчет на странице с доп. инфо"""
    cib_type_id: int
    back: str
    need_add: bool


class UpdateSubOnCIBResearch(CallbackData, prefix=callback_prefixes.UPDATE_CIB_RESEARCH_SUB):
    cib_type_id: int
    need_add: bool
