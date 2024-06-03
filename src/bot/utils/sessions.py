"""Формирование клиентов для работы с http запросами в асинхронном режиме."""
from aiohttp import ClientSession, TCPConnector

from configs.config import (
    BASE_QA_BANKER_URL,
    BASE_STATE_SUPPORT_URL,
    giga_chat_url,
    giga_oauth_url,
)


def singleton(cls):
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
        if not self.session.closed:
            await self.session.close()

    async def recreate(self):
        await self.close()
        self.session = ClientSession(self.base_url, connector=TCPConnector(verify_ssl=False), trust_env=True)


@singleton
class GigaOauthClient(BaseClient):
    """Клиент для получения токена GigaChat."""

    def __init__(self):
        super().__init__(giga_oauth_url)


@singleton
class GigaChatClient(BaseClient):
    """Клиент для получения ответа от GigaChat."""

    def __init__(self):
        super().__init__(giga_chat_url)


@singleton
class RagQaBankerClient(BaseClient):
    """Клиент для получения ответа от RAG по новостям."""

    def __init__(self):
        super().__init__(BASE_QA_BANKER_URL)


@singleton
class RagStateSupportClient(BaseClient):
    """Клиент для получения ответа от RAG по господдержке."""

    def __init__(self):
        super().__init__(BASE_STATE_SUPPORT_URL)
