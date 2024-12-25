"""Вспомогательный функции и классы для работы function calling"""

from langchain_core.runnables.base import Runnable
from langchain_gigachat.chat_models.gigachat import GigaChat
from langchain_openai import ChatOpenAI

from agent_app import logger
from config import API_KEY, BASE_URL, AGENT_MODEL, AGENT_MODEL_TYPE, TEMP, MAX_TOKENS
from config import giga_scope, giga_credentials


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
        logger.error(f"Ошбика при получении ответа от ЛЛМ: {e}")
        return "Ошибка при получении ответа от ЛЛМ"


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
