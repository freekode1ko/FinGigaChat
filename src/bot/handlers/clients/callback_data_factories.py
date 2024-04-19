from aiogram.filters.callback_data import CallbackData


MENU = 'clients_menu'


class Menu(CallbackData, prefix=MENU):
    """
    Клиенты из списка подписок
    Другие клиенты
    """
    pass


class EndMenu(CallbackData, prefix='end_clients_menu'):
    """завершить """
    pass


class SubscribedClients(CallbackData, prefix='subscribed_clients'):
    """Список клиентов из списка подписок"""
    pass


class UnsubscribedClients(CallbackData, prefix='unsubscribed_clients'):
    """Список других клиентов"""
    pass


class ClientMenu(CallbackData, prefix='client_menu'):
    """
    Новости
    Аналитика sell-side [если публичный]  (
        callbacks.GetCIBResearchData.summary_type=enums.ResearchSummaryType.analytical_indicators.value
    )
    Отраслевая аналитика
    Продуктовые предложения
    Цифровая справка
    Сформировать материалы для встречи
    Call-reports
    """
    client_id: int


class ClientNewsMenu(CallbackData, prefix='client_news_menu'):
    """
    Топ новости
    Выбрать период 1, 3, 7, 30 дней
    """
    client_id: int


class IndustryAnalytics(CallbackData, prefix='industry_analytics'):
    """
    Выдача файлов аналитики из раздела отраслевая аналитика той отрасли,
    к которой принадлежит клиент (industry_id)
    """
    industry_id: int


class ClientProducts(CallbackData, prefix='client_products'):
    """Продуктовые предложения по клиенту"""
    client_id: int


class ClientInavigatorLink(CallbackData, prefix='client_inavigator_link'):
    """Цифровая справка"""
    client_id: int


class ClientCallReports(CallbackData, prefix='client_call_reports'):
    """Меню кол-репортов по клиенту"""
    client_id: int
