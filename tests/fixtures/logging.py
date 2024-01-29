import logging

import pytest

from module.logger_base import TelegramLogger


@pytest.fixture
def logger() -> logging.Logger:
    return logging.getLogger('test_logger')


@pytest.fixture
def tg_logger(logger) -> TelegramLogger:
    return TelegramLogger(logger)
