from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_gigachat.chat_models.gigachat import GigaChat

from configs.config import giga_scope, giga_model, giga_credentials
from utils.function_calling.tool_functions.tool_prompts import SUMMARIZATION_SYSTEM, SUMMARIZATION_USER
from utils.function_calling.tool_functions.utils import get_answer_giga


@tool
async def get_recomendation_by_contexts(text: str, config: RunnableConfig):
    """Возвращает рекомендации банковских продуктов по тексту инфоповодов

    Args:
        text (str): инфоповоды про компанию, по которым нужно дать рекомендации по продуктам.
    return:
        (str): Текст с рекомендациями продуктов.
    """
    print(f'Вызвана функция get_recomendation_by_contexts с параметром: {text}')

    llm = GigaChat(base_url='https://gigachat-preview.devices.sberbank.ru/api/v1/',
                   verbose=True,
                   credentials=giga_credentials,
                   scope=giga_scope,
                   model=giga_model,
                   verify_ssl_certs=False,
                   profanity_check=False,
                   temperature=0.00001
                   )
    result = await get_answer_giga(llm, SUMMARIZATION_SYSTEM, SUMMARIZATION_USER, text)
    print('Окончен вызов функции get_recomendation_by_contexts')
    return result
