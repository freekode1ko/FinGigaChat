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


class GetCIBResearchData(CallbackData, prefix=callback_prefixes.RESEARCH_TYPE_INFO):
    """
    Меню для получения отчетов за время
    research_type_id=0 или research_type.id
    summary_type - тип, на основе которого формируется меню или делается выгрузка данных
    """
    research_type_id: int
    summary_type: int


class GetResearchesOverDays(CallbackData, prefix=callback_prefixes.GET_RESEARCHES):
    """Выгрузка отчетов за последние days_count"""
    research_type_id: int
    days_count: int


class GetEconomyDailyResearchesOverDays(CallbackData, prefix=callback_prefixes.GET_ECONOMY_DAILY_RESEARCHES):
    """Выгрузка отчетов за последние days_count"""
    research_type_id: int
    days_count: int


class GetINavigatorSource(CallbackData, prefix=callback_prefixes.GET_CLIENT_INAVIGATOR):
    """Получение справки из INavigator"""
    research_type_id: int


class SelectClientResearchesGettingPeriod(CallbackData, prefix=callback_prefixes.SELECT_CLIENT_RESEARCH_GETTING_PERIOD):
    """
    Меню выбора периода получения отчетов по клиенту
    research_type_id=research_type.id
    summary_type - тип, на основе которого формируется меню или делается выгрузка данных
    """
    research_type_id: int
    summary_type: int


class NotImplementedFunctionality(CallbackData, prefix=callback_prefixes.NOT_IMPLEMENTED):
    """Не реализованный функционал"""
    research_type_id: int
