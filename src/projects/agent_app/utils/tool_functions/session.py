"""Подключения"""

from config import psql_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

engine = create_engine(psql_engine, poolclass=NullPool)
async_engine = create_async_engine(str(psql_engine).replace('postgresql://', 'postgresql+asyncpg://'), poolclass=NullPool)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

from aiohttp import ClientSession, TCPConnector

from config import (
    BASE_QA_BANKER_URL,
    BASE_QA_RESEARCH_URL,
    BASE_QA_WEB_URL,
)


def singleton(cls):
    """Сингелтон"""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class BaseClient:
    """Базовый класс для создания клиентов."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = ClientSession(base_url, connector=TCPConnector(verify_ssl=False), trust_env=True)

    async def close(self):
        """Закрытие соединения"""
        if not self.session.closed:
            await self.session.close()

    async def recreate(self):
        """Пересоздание соединения"""
        await self.close()
        self.session = ClientSession(self.base_url, connector=TCPConnector(verify_ssl=False), trust_env=True)


@singleton
class RagQaBankerClient(BaseClient):
    """Клиент для получения ответа от RAG по новостям."""

    def __init__(self):
        super().__init__(BASE_QA_BANKER_URL)


@singleton
class RagQaResearchClient(BaseClient):
    """Клиент для получения ответа от RAG по CIB Research."""

    def __init__(self):
        super().__init__(BASE_QA_RESEARCH_URL)


@singleton
class RagWebClient(BaseClient):
    """Клиент для получения ответа от web RAG"""

    def __init__(self):
        super().__init__(BASE_QA_WEB_URL)
