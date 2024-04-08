from aiogram.filters.callback_data import CallbackData

from constants.analytics import analytics_sell_side as callback_prefixes


class Menu(CallbackData, prefix=callback_prefixes.MENU):
    pass


class GetCIBGroupSections(CallbackData, prefix=callback_prefixes.SECTIONS):
    """
    Меню разделов для группы group_id
    """
    group_id: int


class GetCIBSectionResearches(CallbackData, prefix=callback_prefixes.RESEARCH_TYPES):
    """
    Меню отчетов для раздела section_id
    """
    section_id: int


class GetCIBResearchType(CallbackData, prefix=callback_prefixes.RESEARCH_TYPE_INFO):
    """Меню для получения отчетов за время"""
    research_type_id: int


class GetResearchesOverDays(CallbackData, prefix=callback_prefixes.GET_RESEARCHES):
    """Выгрузка отчетов за последние days_count"""
    research_type_id: int
    days_count: int
