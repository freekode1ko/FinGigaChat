"""Вспомогательный функции и классы для работы function calling"""

import dataclasses
from typing import Any

from aiogram import types
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.base import Runnable
from langchain_gigachat.chat_models.gigachat import GigaChat
from langchain_openai import ChatOpenAI

from configs.config import giga_scope, giga_credentials
from utils.function_calling.tool_functions.preparing_meeting.config import API_KEY, BASE_URL, AGENT_MODEL, \
    AGENT_MODEL_TYPE, TEMP, MAX_TOKENS


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


async def get_answer_llm(llm: Runnable,
                         system_prompt: str,
                         user_prompt: str,
                         text: str) -> str:
    """
    Асинхронный запрос в модель.

    :param llm: инстанс подключения к ллм.
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


async def send_status_message_for_agent(
        config: RunnableConfig,
        text: str,
        is_start_message: bool = False
):
    """"""
    try:
        message = config['configurable']['message']
        buttons = config['configurable']['buttons']
        message_text = config['configurable']['message_text']
        final_message = config['configurable']['final_message']
        task_text = config['configurable']['task_text']
        tasks_left = config['configurable']['tasks_left']

        message_text.append(f'<b>{text}</b>\n')
        message_text.append(f'<blockquote expandable>{task_text}</blockquote>\n\n')

        await final_message.edit_text(''.join(message_text) + f'🦿Осталось <b>{tasks_left}</b> шагов...', parse_mode='HTML')
    except Exception as e:
        print(e)
        pass


def get_model() -> Runnable:
    """
    Возвращает модель

    :return: модель ллм.
    """
    if AGENT_MODEL == 'gpt':
        llm = ChatOpenAI(model=AGENT_MODEL_TYPE,
                         api_key=API_KEY,
                         base_url=BASE_URL,
                         max_tokens=MAX_TOKENS,
                         temperature=TEMP)
    elif AGENT_MODEL == 'giga':
        llm = GigaChat(verbose=True,
                       credentials=giga_credentials,
                       scope=giga_scope,
                       model=AGENT_MODEL_TYPE,
                       verify_ssl_certs=False,
                       profanity_check=False,
                       temperature=TEMP)
    else:
        raise Exception('Wrong agent model type parameter')
    return llm

