"""Модуль работы с таблицами по RAG  category"""
from sqlalchemy import func, select

from db import database
from db.models import RAGClassificationCategory, RAGClassificationCategoryQuestionExample


def get_rag_categories() -> list[RAGClassificationCategory]:
    """Получить объекты категорий для RAG."""
    with database.engine.connect() as conn:
        return conn.execute(select(RAGClassificationCategory).order_by(RAGClassificationCategory.name)).fetchall()


def get_rag_question_to_categories() -> list[tuple[str, str]]:
    """Получить список вопрос-категория для RAG."""
    with database.engine.connect() as conn:
        subquery = (
            select(
                RAGClassificationCategoryQuestionExample.question,
                RAGClassificationCategory.name,
                func.row_number().over(
                    partition_by=RAGClassificationCategory.id,
                    order_by=RAGClassificationCategoryQuestionExample.question
                ).label('row_number')
            )
            .join(
                RAGClassificationCategory,
                RAGClassificationCategory.id == RAGClassificationCategoryQuestionExample.category_id
            )
            .subquery()
        )
        stmt = select(subquery.c.question, subquery.c.name).where(subquery.c.row_number <= 13)
        return conn.execute(stmt).fetchall()
