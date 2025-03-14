from copy import deepcopy

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from configs import prompts
from constants.enums import RAGCategoryType
from log.bot_logger import logger
from module.llm_langchain import giga
from utils.rag_utils.classification import constants


def get_category_enum_from_value(question: str, value: str) -> RAGCategoryType | None:
    """Получить тип Enum по значению."""
    value = value.lower().strip()
    for enum_member in RAGCategoryType:
        if value in enum_member.value:
            logger.info(f'Для вопроса "{question}" получена группа категорий "{enum_member}"')
            return enum_member
    logger.error(f'Нет группы категорий, соответствующей значению: {value}')
    return None


async def get_category_from_llm(question: str, messages: list[BaseMessage]) -> tuple[str, RAGCategoryType | None]:
    """Получить категорию вопроса от LLM по переданным сообщениям."""
    response = await giga.ainvoke(messages)
    logger.info(f'При классификации вопроса "{question}" на категорию LLM сформировала ответ: "{response}"')
    return response, get_category_enum_from_value(question, response)


async def predict_category_by_question(question: str) -> RAGCategoryType | str | None:
    """Предсказать категорию вопроса."""
    messages = deepcopy(constants.RAG_CLASSIFICATION_MESSAGES) + [HumanMessage(question)]
    _, category = await get_category_from_llm(question, messages)
    return category or await predict_category_by_question_short_way(question)


async def predict_category_by_question_short_way(question: str):
    """
    Есть случаи, когда классификатор начинает отвечать на вопрос. В таком
    случае стараемся принудительно предсказывать категорию"""
    messages = [constants.RAG_CLASSIFICATION_SYSTEM_MESSAGE, HumanMessage(question)]
    giga_response, category = await get_category_from_llm(question, messages)
    if category:
        return category

    messages.extend([
        AIMessage(giga_response),
        HumanMessage(
            prompts.CLASSIFICATION_EXTRA_HUMAN_PROMPT.format(
                categories='\n'.join(constants.RAG_CLASSIFICATION_CATEGORIES_NAMES.keys())
            )
        )
    ])
    _, category = await get_category_from_llm(question, messages)
    return category or RAGCategoryType.other
