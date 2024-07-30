"""Реализация ограничителя по отправки сообщений в ТГ"""

import asyncio
from contextlib import AbstractAsyncContextManager
from types import TracebackType
from typing import Dict, Optional, Type

from configs.config import NUBER_OF_MESSAGES_TG_BOT_CAN_SEND


class AsyncLimiter(AbstractAsyncContextManager):
    """A leaky bucket rate limiter."""

    def __init__(self, max_rate: float, time_period_sec: float = 1) -> None:
        self.max_rate = max_rate
        self.time_period_sec = time_period_sec
        self._rate_per_sec = max_rate / time_period_sec
        self._level = 0.0
        self._last_check = 0.0
        # queue of waiting futures to signal capacity to
        self._waiters: Dict[asyncio.Task, asyncio.Future] = {}

    def _leak(self) -> None:
        """Drip out capacity from the bucket."""
        loop = asyncio.get_running_loop()
        if self._level:
            # drip out enough level for the elapsed time since
            # we last checked
            elapsed = loop.time() - self._last_check
            decrement = elapsed * self._rate_per_sec
            self._level = max(self._level - decrement, 0)
        self._last_check = loop.time()

    def has_capacity(self, amount: float = 1) -> bool:
        """Check if there is enough capacity remaining in the limiter

        :param amount: How much capacity you need to be available.

        """
        self._leak()
        requested = self._level + amount
        # if there are tasks waiting for capacity, signal to the first
        # there may be some now (they won't wake up until this task
        # yields with an await)
        if requested < self.max_rate:
            for fut in self._waiters.values():
                if not fut.done():
                    fut.set_result(True)
                    break
        return self._level + amount <= self.max_rate

    async def acquire(self, amount: float = 1) -> None:
        """Acquire capacity in the limiter.

        If the limit has been reached, blocks until enough capacity has been
        freed before returning.

        :param amount: How much capacity you need to be available.
        :exception: Raises :exc:`ValueError` if `amount` is greater than
           :attr:`max_rate`.

        """
        if amount > self.max_rate:
            raise ValueError("Can't acquire more than the maximum capacity")

        loop = asyncio.get_running_loop()
        if (task := asyncio.current_task(loop)) is None:
            raise Exception

        while not self.has_capacity(amount):
            # wait for the next drip to have left the bucket
            # add a future to the _waiters map to be notified
            # 'early' if capacity has come up
            fut = loop.create_future()
            self._waiters[task] = fut
            try:
                await asyncio.wait_for(asyncio.shield(fut), 1 / self._rate_per_sec * amount)
            except asyncio.TimeoutError:
                pass
            fut.cancel()
        self._waiters.pop(task, None)

        self._level += amount

        return None

    async def __aenter__(self) -> None:
        """Async enter context"""
        await self.acquire()
        return None

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None:
        """Async exit context"""
        return None


limiter = AsyncLimiter(max_rate=NUBER_OF_MESSAGES_TG_BOT_CAN_SEND)
