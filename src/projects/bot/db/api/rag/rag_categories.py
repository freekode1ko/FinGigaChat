"""Модуль работы с таблицами по RAG  category"""
from sqlalchemy import select

from db import database
from db.models import RAGClassificationCategory, RAGClassificationCategoryQuestionExample


def get_rag_categories() -> list[RAGClassificationCategory]:
    """Получить объекты категорий для RAG."""
    with database.engine.connect() as conn:
        return conn.execute(select(RAGClassificationCategory).order_by(RAGClassificationCategory.name)).fetchall()


def get_rag_question_to_categories() -> list[tuple[str, str]]:
    """Получить список вопрос-категория для RAG."""
    with database.engine.connect() as conn:
        stmt = (
            select(RAGClassificationCategoryQuestionExample.question, RAGClassificationCategory.name)
            .join(
                RAGClassificationCategory,
                RAGClassificationCategory.id == RAGClassificationCategoryQuestionExample.category_id
            )
        )
        return conn.execute(stmt).fetchall()
