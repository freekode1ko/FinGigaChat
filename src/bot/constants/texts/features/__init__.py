"""Пакет с текстовыми константами для функционала бота."""
from constants.texts.features.ai import CallReportsTexts, RAGTexts
from constants.texts.features.analytics import AnalyticsSellSide
from constants.texts.features.common import CommonTexts, HelpTexts, RegistrationTexts
from constants.texts.features.news import CibResearchTexts, FuzzySearchTexts, StakeholderTexts
from constants.texts.features.subjects import ClientInfoTexts
from constants.texts.features.utils import TelegramMessageParams, WatermarkConfig

CONFIG_CLASSES = [
    AnalyticsSellSide,
    CallReportsTexts,
    CommonTexts,
    CibResearchTexts,
    ClientInfoTexts,
    HelpTexts,
    RAGTexts,
    RegistrationTexts,
    FuzzySearchTexts,
    StakeholderTexts,
    TelegramMessageParams,
    WatermarkConfig,
]

__all__ = [
    CONFIG_CLASSES,
]
