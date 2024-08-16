"""Модуль для текстовок."""
from pydantic_settings import BaseSettings


class TelegramNewsTexts(BaseSettings):
    """Класс для текстовок телеграммных новостей."""

    TELEGRAM_NEWS_START: str = 'Выберите раздел для получения краткой сводки новостей из telegram каналов'

    TELEGRAM_NEWS_CHOOSE_PERIOD: str = (
        'Выберите период, за который хотите получить сводку новостей из telegram каналов по разделу '
        '<b>{section}</b>\n\n'
        'Для получения новостей из telegram каналов, на которые вы подписались в боте, выберите '
        '<b>"{my_industry_callback}"</b>\n'
        'Для получения новостей из всех telegram каналов, связанных с разделом, выберите '
        '<b>"{all_industry_callback}"</b>'
    )
