import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection, async_sessionmaker

from app import app
from db.database import get_async_session
from db.models import Base
from tests.constants import MOCK_REG_CODE

# Database URL for testing
DATABASE_TEST_URL = "postgresql://postgres:postgres@127.0.0.1:5555/test_db"


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("PSQL_ENGINE", DATABASE_TEST_URL)


@pytest.fixture(scope='session')
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def _db_connection():
    async_engine = create_async_engine(
        str(DATABASE_TEST_URL).replace('postgresql://', 'postgresql+asyncpg://'),
        echo=False,
        future=True,
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def _async_session(
        _db_connection: AsyncConnection,
) -> AsyncGenerator[AsyncSession, None]:
    session = async_sessionmaker(
        bind=_db_connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session() as s:
        yield s


@pytest_asyncio.fixture(scope="function")
async def _async_client(_async_session: AsyncSession):
    app.dependency_overrides[get_async_session] = lambda: _async_session
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://localhost:8000',
    ) as client:
        yield client


@pytest.fixture
def mock_redis_client():
    client = AsyncMock()
    client.get.return_value = MOCK_REG_CODE
    client.setex.return_value = True
    client.delete.return_value = True
    return client


@pytest.fixture
def mock_smtp_send():
    smtp_send = AsyncMock()
    smtp_send.send_msg.return_value = True
    return smtp_send




# @pytest_asyncio.fixture(scope="function")
# async def _async_client(_async_session: AsyncSession):
#     # TODO: нашел этот код, возможно для чего-то использовалось
#     # app.dependency_overrides[get_async_session] = lambda: _async_session
#
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as client:
#         yield client

#
#
# # Create tables in the database
# # Base.metadata.create_all(bind=async_engine)
#
#
# @pytest.fixture(scope="function")
# def db_session():
#     """Create a new database session with a rollback at the end of the test."""
#     connection = async_engine.connect()
#     transaction = connection.begin()
#     session = async_session(bind=connection)
#     yield session
#     session.close()
#     transaction.rollback()
#     connection.close()
