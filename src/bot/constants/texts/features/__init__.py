"""Пакет с текстовыми константами для функционала бота."""
from constants.texts.features.ai import *
from constants.texts.features.news import *
from constants.texts.features.utils import *

CONFIG_CLASSES = [
    CallReportsTexts,
    StakeholderTexts,
    WatermarkConfig,
]

__all__ = [
    CONFIG_CLASSES,
]
