"""CallbackData по подпискам на CIB"""
from aiogram.filters.callback_data import CallbackData

from constants.subscriptions import research as callback_prefixes
from keyboards.subscriptions import callbacks


class GetUserCIBResearchSubs(CallbackData, prefix=callback_prefixes.USER_CIB_RESEARCH_SUBS):
    """
    Подписки пользователя на отчеты CIB

    Если delete_sub_id != 0, то удаление подписки
    """

    page: int = 0
    del_sub_id: int = 0
    action: callbacks.SubsMenusEnum = callbacks.SubsMenusEnum.my_subscriptions


class GetCIBResearchTypeMoreInfo(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_INFO):
    """Доп. инфо по отчету, на который можно подписаться"""

    research_id: int
    is_subscribed: bool = False
    back: str


class GetCIBGroups(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_GROUPS_MENU):
    """Меню групп"""

    pass


class GetCIBSectionResearches(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_SECTION_RESEARCHES_MENU):
    """
    Меню отчетов для раздела section_id

    Подписка/отписка на отчет research_id, если research_id != 0
    """

    group_id: int
    section_id: int
    research_id: int = 0
    need_add: int = 0


class GetCIBGroupSections(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_GROUP_SECTIONS_MENU):
    """
    Меню разделов для группы group_id

    Если у группы dropdown_flag установлен в False, то пользователь может подписаться на раздел
    Если section_id != 0, то подписка(need_add) или отписка(!need_add)
    """

    group_id: int
    section_id: int = 0
    need_add: int = 0


class CIBResearchSubAction(CallbackData, prefix=callback_prefixes.CIB_RESEARCH_SUB_ACTION):
    """Подписка/отписка на отчет на странице с доп. инфо"""

    research_id: int
    back: str
    need_add: bool


class UpdateSubOnCIBResearch(CallbackData, prefix=callback_prefixes.UPDATE_CIB_RESEARCH_SUB):
    """Обновление подписки на отчет"""

    cib_type_id: int
    need_add: bool
