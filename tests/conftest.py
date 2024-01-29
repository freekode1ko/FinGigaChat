import asyncio
import typing as t

import pytest

pytest_plugins = ['tests.fixtures']


@pytest.fixture(scope='session')
def event_loop() -> t.Iterator[asyncio.AbstractEventLoop]:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # pytest-aiohttp may conflict if not specified
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    yield loop
    loop.close()
