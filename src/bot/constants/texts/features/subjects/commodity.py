"""Модуль с текстовыми константами по взаимодействию с коммодами."""
from pydantic_settings import BaseSettings


class CommodityTexts(BaseSettings):
    """Класс с текстовками по данным о коммодах."""

    COMMODITY_CHOOSE_SECTION: str = 'Выберите раздел для получения данных по по сырьевому товару <b>{name}</b>'

    COMMODITY_END: str = 'Просмотр по сырьевому товару завершен'

    COMMODITY_CHOOSE_PERIOD: str = 'Выберите период для получения новостей по сырьевому товару <b>{name}</b>'

    COMMODITY_PERIOD_ARTICLES: str = 'Новости по сырьевому товару <b>{name}</b> за {days} дней\n'
