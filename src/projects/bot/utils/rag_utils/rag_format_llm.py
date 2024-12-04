"""Форматирование финального ответа с помощью llm"""

from langchain_openai import ChatOpenAI
from langchain_gigachat.chat_models.gigachat import GigaChat

from configs.config import giga_credentials, giga_scope, giga_model, BASE_GPT_MODEL, BASE_GPT_URL, OPENAI_API_KEY
from configs.prompts import RESTYLE_PROMPT_SYSTEM, RESTYLE_PROMPT_USER

gpt = ChatOpenAI(model=BASE_GPT_MODEL,
                 api_key=OPENAI_API_KEY,
                 base_url=BASE_GPT_URL,
                 temperature=0)

giga = GigaChat(base_url='https://gigachat-preview.devices.sberbank.ru/api/v1/',
                verbose=True,
                credentials=giga_credentials,
                scope=giga_scope,
                model=giga_model,
                verify_ssl_certs=False,
                profanity_check=False,
                temperature=0.00001
                )


async def get_format_llm(text: str,
                         llm=gpt,
                         system_prompt: str = RESTYLE_PROMPT_SYSTEM,
                         user_prompt: str = RESTYLE_PROMPT_USER) -> str:
    """
    Асинхронный запрос в ллм.

    :param text: текст пользовательского сообщения.
    :param llm: инстанс подключения к ллм.
    :param system_prompt: системный промпт задачи.
    :param user_prompt: шаблон пользовательского сообщения.
    :return: ответ от гигачата.
    """
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt.format(text=text)}]
    try:
        response = await llm.ainvoke(messages)
        content = response.content
        return content
    except Exception as e:
        print(f"Ошибка при получении ответа от llm: {e}")
        return text
