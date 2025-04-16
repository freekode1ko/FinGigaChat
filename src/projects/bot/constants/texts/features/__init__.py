"""Пакет с текстовыми константами для функционала бота."""
from pydantic_settings import BaseSettings

from constants.texts.features.ai import CallReportsTexts, GagsTexts, RAGTexts, GenAiTexts
from constants.texts.features.analytics import AnalyticsTexts
from constants.texts.features.broadcast import BroadcastTexts
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

CONFIG_CLASSES: list[type[BaseSettings]] = [
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
    BroadcastTexts,
    GagsTexts,
    GenAiTexts,
]

__all__ = [
    CONFIG_CLASSES,
]
