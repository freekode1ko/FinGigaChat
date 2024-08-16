"""Пакет с текстовыми константами по новостям."""
from constants.texts.features.news.cib_research import CibResearchTexts
from constants.texts.features.news.fuzzy_search import FuzzySearchTexts
from constants.texts.features.news.stakeholder import StakeholderTexts
from constants.texts.features.news.telegram_news import TelegramNewsTexts

__all__ = [
    'CibResearchTexts',
    'FuzzySearchTexts',
    'TelegramNewsTexts',
    'StakeholderTexts',
]
