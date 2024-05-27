"""Формирование клиентов для работы с http запросами в асинхронном режиме."""
from aiohttp import ClientSession, TCPConnector


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
        self.session = ClientSession(base_url, connector=TCPConnector(ssl=False))

    async def close(self):
        if not self.session.closed:
            await self.session.close()

    async def recreate(self):
        await self.close()
        self.session = ClientSession(self.base_url, connector=TCPConnector(ssl=False))


@singleton
class GigaOauthClient(BaseClient):
    """Клиент для получения токена GigaChat."""
    pass


@singleton
class GigaChatClient(BaseClient):
    """Клиент для получения ответа от GigaChat."""
    pass


@singleton
class RagQaBankerClient(BaseClient):
    """Клиент для получения ответа от RAG по новостям."""
    pass


@singleton
class RagStateSupportClient(BaseClient):
    """Клиент для получения ответа от RAG по господдержке."""
    pass
