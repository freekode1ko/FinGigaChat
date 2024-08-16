"""Пакет с текстовыми константами для функционала бота."""
from constants.texts.features.ai import CallReportsTexts, RAGTexts
from constants.texts.features.analytics import AnalyticsTexts
from constants.texts.features.common import CommonTexts, HelpTexts, RegistrationTexts
from constants.texts.features.news import CibResearchTexts, FuzzySearchTexts, StakeholderTexts, TelegramNewsTexts
from constants.texts.features.subjects import ClientTexts, CommodityTexts
from constants.texts.features.utils import TelegramMessageParams, WatermarkConfig

CONFIG_CLASSES = [
    AnalyticsTexts,
    CallReportsTexts,
    CibResearchTexts,
    ClientTexts,
    CommodityTexts,
    CommonTexts,
    HelpTexts,
    RAGTexts,
    RegistrationTexts,
    FuzzySearchTexts,
    TelegramNewsTexts,
    StakeholderTexts,
    TelegramMessageParams,
    WatermarkConfig,
]

__all__ = [
    CONFIG_CLASSES,
]
