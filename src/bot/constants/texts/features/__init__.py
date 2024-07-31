"""Пакет с текстовыми константами для функционала бота."""
from constants.texts.features.ai import CallReportsTexts
from constants.texts.features.news import CibResearchTexts, FuzzySearchTexts, StakeholderTexts
from constants.texts.features.utils import TelegramMessageParams, WatermarkConfig

CONFIG_CLASSES = [
    CallReportsTexts,
    CibResearchTexts,
    FuzzySearchTexts,
    StakeholderTexts,
    TelegramMessageParams,
    WatermarkConfig,
]

__all__ = [
    CONFIG_CLASSES,
]
