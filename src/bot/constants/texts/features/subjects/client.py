"""Модуль с текстовыми константами по взаимодействию с клиентами."""
from pydantic_settings import BaseSettings

from constants.texts.features import CommonTexts


class ClientTexts(BaseSettings):
    """Класс с текстовками по данным о клиентах."""

    CLIENT_START: str = 'Клиенты'

    CLIENT_END: str = 'Просмотр клиентов завершен'

    CLIENT_CHOOSE_SECTION: str = 'Выберите раздел для получения данных по клиенту <b>{name}</b>'

    CLIENT_CHOOSE_FROM_LIST: str = 'Выберите клиента из списка'

    CLIENT_WRITE_NAME: str = 'Для поиска введите сообщение с именем клиента.'

    CLIENT_CHOOSE_SUBS_CLIENT: str = 'Выберите клиента из списка ваших подписок\n<b>{page_info}</b>\n\n' + CLIENT_WRITE_NAME

    CLIENT_NOT_FOUND: str = 'Не нашелся, введите имя клиента по-другому'

    CLIENT_WHAT_NEWS: str = 'Какие новости вы хотите получить по клиенту <b>{name}</b>'

    CLIENT_INDUSTRY_ANAL: str = 'Отраслевая аналитика по клиенту <b>{name}</b>\n'

    CLIENT_PRODUCT: str = 'Продуктовые предложения по клиенту <b>{name}</b>'

    CLIENT_MEETING_DATA: str = 'Материалы для встречи по клиенту <b>{name}</b>\n' + CommonTexts().COMMON_FEATURE_WILL_APPEAR

    CLIENT_TOP_ARTICLES: str = 'Топ новости по клиенту <b>{}</ b>\n' + CommonTexts().COMMON_FEATURE_WILL_APPEAR

    CLIENT_CHOOSE_PERIOD: str = 'Выберите период для получения новостей по клиенту <b>{name}</b>'

    CLIENT_PERIOD_ARTICLES: str = 'Новости по клиенту <b>{name}</b> за {days} дней\n'
