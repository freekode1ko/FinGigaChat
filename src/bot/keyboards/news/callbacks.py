"""Клавиатуры для новостей"""
from aiogram.filters.callback_data import CallbackData


class GetClientNews(CallbackData, prefix='get_client_news'):
    """Получение новостей по клиенту"""

    subject_id: int


class GetCommodityNews(CallbackData, prefix='get_commodity_news'):
    """Получение новостей по сырьевому товару"""

    subject_id: int


class GetIndustryNews(CallbackData, prefix='get_industry_news'):
    """Получение новостей по отрасли"""

    subject_id: int
