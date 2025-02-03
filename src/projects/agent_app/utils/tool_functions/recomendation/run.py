"""Рекомендация продуктов"""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from agent_app import logger
from utils.tool_functions.tool_prompts import RECOMENDATION_SYSTEM, RECOMENDATION_USER
from utils.tool_functions.utils import get_answer_llm, get_model


# TODO: здесь должен когда-то повявиться нормальный рексис..
@tool
async def get_recomendation_by_contexts(text: str, config: RunnableConfig):
    """Возвращает рекомендации банковских продуктов по тексту инфоповодов

    Args:
        text (str): инфоповоды про компанию, по которым нужно дать рекомендации по продуктам.
    return:
        (str): Текст с рекомендациями продуктов.
    """
    logger.info(f'Вызвана функция get_recomendation_by_contexts с параметром: {text}')

    llm = get_model()
    result = await get_answer_llm(llm, RECOMENDATION_SYSTEM, RECOMENDATION_USER, text)
    return result
