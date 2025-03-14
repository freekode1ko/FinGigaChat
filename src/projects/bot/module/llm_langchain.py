import asyncio

from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from openai import RateLimitError
from gigachat.exceptions import ResponseError
from langchain_gigachat import GigaChat

from configs import config
from log.bot_logger import logger

__all__ = ['giga']


class BaseLLM:

    MAX_RETRIES = 3
    BACKOFF_FACTOR = 1

    def __init__(self, client: BaseChatModel):
        logger.info(f'Инициализация клиента {self}')
        self.client = client

    def __str__(self):
        return self.__class__.__name__

    async def ainvoke(self, messages: list[BaseMessage]) -> str | None:
        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.ainvoke(messages)
                return response.content

            except (ResponseError, RateLimitError) as e:
                if isinstance(e, ResponseError):
                    error_args = e.args
                    if len(error_args) < 2 or error_args[1] != 429:
                        logger.error(f'Неизвестная ошибка {type(e)} по запросу {self}: {messages}: {e}')
                        break

                wait_time = self.BACKOFF_FACTOR * (2 ** attempt)
                logger.warning(f'TooManyRequests, повтор через {wait_time} сек. Попытка {attempt + 1}/{self.MAX_RETRIES}')
                await asyncio.sleep(wait_time)

            except Exception as e:
                logger.error(f'Неизвестная ошибка {type(e)} по запросу {self}: {messages}: {e}')
                break

        return None


giga_client = GigaChat(
    credentials=config.giga_credentials,
    scope=config.giga_scope,
    model=config.giga_model_max,
    temperature=1e-5,
    max_tokens=2_000,
    verify_ssl_certs=False,
    profanity_check=False,
)

giga = BaseLLM(giga_client)
