"""Константы-промпты для классификации вопросов."""
import random

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from sklearn.model_selection import StratifiedKFold

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
    question_to_categories = get_rag_question_to_categories()
    categories = [qc[1] for qc in question_to_categories]

    kf = StratifiedKFold(n_splits=3, shuffle=True, random_state=1337)
    messages = []
    for train_index, test_index in kf.split(categories, y=categories):
        train_index, test_index = test_index, train_index
        random.shuffle(train_index)

        messages = [RAG_CLASSIFICATION_SYSTEM_MESSAGE]
        for i in train_index:
            question, category = question_to_categories[i]
            messages.append(HumanMessage(question))
            messages.append(AIMessage(category))
    return messages


RAG_CLASSIFICATION_MESSAGES = make_classification_messages()
