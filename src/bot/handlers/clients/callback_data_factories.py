"""CallbackData клиентов"""
from enum import auto, IntEnum

from aiogram.filters.callback_data import CallbackData

from constants.enums import FinancialIndicatorsType

MENU = 'clients_menu'


class ClientsMenusEnum(IntEnum):
    """Уровни меню клиенты"""

    main_menu = auto()
    end_menu = auto()

    # переход из main_menu
    clients_list = auto()

    # переход из клиента в clients_list
    client_menu = auto()

    # переходы из client_menu
    client_news_menu = auto()  # Меню получения новостей по клиенту
    analytic_indicators = auto()  # (FROM ANOTHER MENU) аналитические данные по клиенту, если есть research_type_id
    industry_analytics = auto()  # (FROM ANOTHER MENU) выдача файлов отрасли (отраслевая аналитика), к которой принадлежит клиент
    products = auto()  # Меню продуктовых предложений по клиенту
    inavigator = auto()  # выдача inavigator
    meetings_data = auto()  # материалы для встреч
    call_reports = auto()  # (FROM ANOTHER MENU) call reports по клиенту

    # переходы из client_news_menu
    top_news = auto()  # Выдача топ новостей
    select_period = auto()  # Меню выбора периода для выгрузки новостей

    # переходы из products
    hot_offers = auto()  # Выдача hot offers

    # Новости за период (переход из news_by_period)
    news_by_period = auto()

    # Вывод сообщения, то функционал не готов
    not_implemented = auto()

    # Получение фин показателей по клиенту
    financial_indicators = auto()

    # Меню периодов для получения отчетов CIB Research по клиенту
    analytic_reports = auto()

    # Выгрузка отчетов за период
    get_anal_reports = auto()

    # меню для стейкхолдеров
    choose_stakeholder_clients = auto()  # выбор клиентов стейкхолдера
    show_news_from_sh = auto()  # выдача новостей по всем клиентам стейкхолдера


class ClientsMenuData(CallbackData, prefix=MENU):
    """Меню клиенты"""

    menu: ClientsMenusEnum
    subscribed: bool = True
    client_id: int = 0
    research_type_id: int = 0
    days_count: int = 1
    page: int = 0
    fin_indicator_type: FinancialIndicatorsType | None = None
