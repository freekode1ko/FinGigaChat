"""Мидлвейр для запросов к БД"""
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для создания БД сессии"""

    def __init__(self, session_maker: async_sessionmaker) -> None:
        self.session_maker = session_maker

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]) -> Any:
        """Создания БД сессии"""
        async with self.session_maker() as session:
            data['session'] = session
            return await handler(event, data)
