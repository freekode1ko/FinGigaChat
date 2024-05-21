"""Методы по взаимодействию с таблицей UserRagFeedback в БД."""
import datetime

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert as insert_pg

from constants.enums import RetrieverType
from db.database import async_session
from db.models import RAGUserFeedback


async def add_rag_activity(
        chat_id: int,
        bot_msg_id: int,
        retriever_type: RetrieverType,
        date: datetime,
        query: str,
        rephrase_query: str,
        response: str
):
    """
    Логирование использования RAG-системы.

    :param chat_id:         Id чата с пользователем.
    :param bot_msg_id:      Id сообщения от бота.
    :param retriever_type:  Тип ретривера.
    :param date:            Дата+время ответа сообщения от бота.
    :param query:           Запрос пользователя.
    :param rephrase_query:  Перефразированный с помощью GigaChat запрос пользователя.
    :param response:        Ответ ретривера (сообщение от бота).
    """
    stmt = insert_pg(RAGUserFeedback).values(
        chat_id=chat_id,
        bot_msg_id=bot_msg_id,
        retriever_type=retriever_type.name,
        date=date.replace(tzinfo=None),
        query=query,
        rephrase_query=rephrase_query,
        response=response
    )
    stmt = stmt.on_conflict_do_update(
        constraint="rag_user_feedback_pkey",
        set_={
            "chat_id": stmt.excluded.chat_id,
            "bot_msg_id": stmt.excluded.bot_msg_id,
            "retriever_type": retriever_type.name,
            "response": response,
        }
    )
    async with async_session() as session:
        await session.execute(stmt)
        await session.commit()


async def update_user_reaction(chat_id: int, bot_msg_id: int, reaction: bool):
    """
    Добавление обратной связи от пользователя по использованию RAG-системы.

    :param chat_id:     Id чата с пользователем.
    :param bot_msg_id:  Id сообщения от бота.
    :param reaction:    Реакция пользователя на ответ RAG-системы (True/False).
    """
    stmt = (
        update(RAGUserFeedback)
        .where(RAGUserFeedback.chat_id == chat_id, RAGUserFeedback.bot_msg_id == bot_msg_id)
        .values(reaction=reaction)
    )
    async with async_session() as session:
        await session.execute(stmt)
        await session.commit()
