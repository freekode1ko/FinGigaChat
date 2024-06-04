"""Мидлвейр для логирования"""
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]) -> Any:
        data['logger'] = self.logger
        return await handler(event, data)
