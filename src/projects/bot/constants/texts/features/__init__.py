"""Пакет с текстовыми константами для функционала бота."""
from constants.texts.features.ai import CallReportsTexts, RAGTexts
from constants.texts.features.analytics import AnalyticsTexts
from constants.texts.features.common import CommonTexts, HelpTexts, RegistrationTexts
from constants.texts.features.news import (
    CibResearchTexts,
    FuzzySearchTexts,
    NewsTexts,
    StakeholderTexts,
    TelegramNewsTexts,
)
from constants.texts.features.subjects import ClientTexts, CommodityTexts
from constants.texts.features.utils import TelegramMessageParams, WatermarkConfig
from constants.texts.features.web_app import TelegramWebAppParams

CONFIG_CLASSES = [
    AnalyticsTexts,
    CallReportsTexts,
    CibResearchTexts,
    ClientTexts,
    CommodityTexts,
    CommonTexts,
    FuzzySearchTexts,
    HelpTexts,
    NewsTexts,
    RAGTexts,
    RegistrationTexts,
    StakeholderTexts,
    TelegramMessageParams,
    TelegramNewsTexts,
    WatermarkConfig,
    TelegramWebAppParams,
]

__all__ = [
    CONFIG_CLASSES,
]
