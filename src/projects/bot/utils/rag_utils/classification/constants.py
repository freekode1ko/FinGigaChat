"""Константы-промпты для классификации вопросов."""
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from configs import prompts
from db.api.rag.rag_categories import get_rag_categories, get_rag_question_to_categories


__all__ = [
    'RAG_CLASSIFICATION_CATEGORIES_NAMES',
    'RAG_CLASSIFICATION_SYSTEM_MESSAGE',
    'RAG_CLASSIFICATION_MESSAGES'
]


RAG_CLASSIFICATION_CATEGORIES = get_rag_categories()
RAG_CLASSIFICATION_CATEGORIES_NAMES = {category.name: category.id for category in RAG_CLASSIFICATION_CATEGORIES}


def make_classification_system_msg() -> SystemMessage:
    """Создать сообщение с системным промптом для классификации вопросов RAG."""
    prompt = prompts.START_OF_CLASSIFICATION_SYSTEM_PROMPT
    for category in RAG_CLASSIFICATION_CATEGORIES:
        prompt += prompts.CATEGORY_TEMPLATE_OF_CLASSIFICATION_SYSTEM_PROMPT.format(
            category=category.name,
            description=category.description,
            key_words=category.key_words
        )
    return SystemMessage(prompt)


RAG_CLASSIFICATION_SYSTEM_MESSAGE = make_classification_system_msg()


def make_classification_messages() -> list[BaseMessage]:
    """Создать список сообщений из системного промпта и few-shots."""
    messages = [RAG_CLASSIFICATION_SYSTEM_MESSAGE, ]
    question_to_categories = get_rag_question_to_categories()
    for qc in question_to_categories:
        question, category = qc
        messages.append(HumanMessage(question))
        messages.append(AIMessage(category))
    return messages


RAG_CLASSIFICATION_MESSAGES = make_classification_messages()
