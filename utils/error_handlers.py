import logging
from typing import Callable, Optional, Tuple, TypeVar

from aiogram.exceptions import AiogramError, TelegramBadRequest

LoggerT = Optional[logging.Logger]
TelegramErrorT = TypeVar('TelegramErrorT', bound=AiogramError)
TelegramErrorHandlerT = Callable[[TelegramErrorT, LoggerT], bool]

__all__ = ['handle_telegram_bad_request_error', 'handle_message_too_long_error']


def handle_message_too_long_error(err: TelegramBadRequest, logger: Optional[logging.Logger] = None) -> bool:
    """
    Хендлер для ошибки message is too long
    Args:
        err - Ошибка от aiogram
    Returns:
        False, если ошибка не относится к message is too long
        True, если ошибка была обработана
    """

    logger = logger or logging.getLogger(__name__)
    if 'text is too long' in err.message:
        logger.error('MessageIsTooLong ERROR: %s', err.method.text)
        return True
    return False


def handle_telegram_bad_request_error(err: TelegramBadRequest, logger: Optional[logging.Logger] = None) -> bool:
    _errors_handlers: Tuple[TelegramErrorHandlerT] = (handle_message_too_long_error,)
    logger = logger or logging.getLogger(__name__)

    handled = (handler(err, logger) for handler in _errors_handlers)
    if not any(handled):
        logger.error('Error while processing Telegram Error: %s', err)
        raise err
