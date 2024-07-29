"""Пакет с текстовыми константами для функционала бота."""
from constants.texts.features.ai import CallReportsTexts
from constants.texts.features.news import StakeholderTexts
from constants.texts.features.utils import WatermarkConfig

CONFIG_CLASSES = [
    CallReportsTexts,
    StakeholderTexts,
    WatermarkConfig,
]

__all__ = [
    CONFIG_CLASSES,
]
