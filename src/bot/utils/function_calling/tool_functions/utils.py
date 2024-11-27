"""Вспомогательный функции и классы для работы function calling"""

import dataclasses
from typing import Any

import langchain_gigachat
from aiogram import types
from langchain_core.runnables import RunnableConfig


@dataclasses.dataclass
class LanggraphConfig:
    """Клас для хранения конфига langchain"""

    message: types.Message

    def config_to_langgraph_format(self) -> dict[str, dict[str, Any]]:
        """Превращает конфиг из класса в словарь для langgraph"""
        return {'configurable': self.__dict__}


def parse_runnable_config(config: RunnableConfig) -> LanggraphConfig:
    """Превращает RunnableConfig, который получают тузлы, в dataclass"""
    return LanggraphConfig(
        **{
            k: v
            for k, v in config['configurable'].items()
            if k in LanggraphConfig.__dataclass_fields__ and isinstance(v, LanggraphConfig.__dataclass_fields__[k].type)
        }
    )


async def get_answer_giga(llm: langchain_gigachat.chat_models.gigachat.GigaChat,
                          system_prompt: str,
                          user_prompt: str,
                          text: str) -> str:
    """
    Асинхронный запрос в Гигачат.

    :param llm: инстанс подключения к гигачату.
    :param system_prompt: системный промпт задачи.
    :param user_prompt: шаблон пользовательского сообщения.
    :param text: текст пользовательского сообщения.
    :return: ответ от гигачата.
    """
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt.format(text=text)}]
    try:
        response = await llm.ainvoke(messages)
        content = response.content
        return content
    except Exception as e:
        print(f"Ошбика при получении ответа от Гигачата: {e}")
        return "Ошибка при получении ответа от Гигачата"
