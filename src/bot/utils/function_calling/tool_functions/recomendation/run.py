from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from utils.function_calling.tool_functions.preparing_meeting.config import DEBUG_GRAPH, MESSAGE_RUN_PRODUCT_RECOMMENDATION
from utils.function_calling.tool_functions.tool_prompts import SUMMARIZATION_SYSTEM, SUMMARIZATION_USER
from utils.function_calling.tool_functions.utils import get_answer_llm, get_model, send_status_message_for_agent


@tool
async def get_recommendation_by_contexts(text: str, config: RunnableConfig):
    """Возвращает рекомендации банковских продуктов по тексту инфоповодов

    Args:
        text (str): инфоповоды про компанию, по которым нужно дать рекомендации по продуктам.
    return:
        (str): Текст с рекомендациями продуктов.
    """
    if DEBUG_GRAPH:
        print(f'Вызвана функция get_recommendation_by_contexts с параметром: {text}')

    llm = get_model()
    result = await get_answer_llm(llm, SUMMARIZATION_SYSTEM, SUMMARIZATION_USER, text)
    await send_status_message_for_agent(config, MESSAGE_RUN_PRODUCT_RECOMMENDATION)
    return result
