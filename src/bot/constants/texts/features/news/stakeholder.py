"""Модуль с текстовками по новостям о стейкхолдерах."""
from pydantic_settings import BaseSettings


class StakeholderTexts(BaseSettings):
    """Класс с текстовками по новостям о стейкхолдерах."""

    # Текстовки для отображения меню новостей по стейкхолдерам
    BEN_MENU_NEWS: str = 'Выберите наименования, для получения информации'
    LPR_MENU_NEWS: str = 'Выберите наименования, для получения информации'
    COMMON_MENU_NEWS: str = 'Выберите наименования, для получения информации'

    # Ссылка на биографию стейкхолдера
    BIO_LINK: str = ' <a href="{link}">forbes.ru</a>'

    # Текстовки для отображения новостей
    FEW_BEN_SHOW_NEWS: str = 'Вот новости по компаниям'
    FEW_LPR_SHOW_NEWS: str = 'Вот новости по компаниям'
    FEW_COMMON_SHOW_NEWS: str = 'Вот новости по компаниям'
    ONE_BEN_SHOW_NEWS: str = 'Вот новости по компании'
    ONE_LPR_SHOW_NEWS: str = 'Вот новости по <b>{client}</b>'
    ONE_COMMON_SHOW_NEWS: str = 'Вот новости по компании'

    # Сообщение для отображения меню по клиенту
    CLIENT_MENU_START: str = 'Дополнительные данные о клиенте <b>{client}</b>'
