"""Методы по взаимодействию с таблицей UserRagFeedback в БД."""
import datetime

from sqlalchemy import insert, update

from constants.enums import RetrieverType
from db.database import async_session
from db.models import RAGUserFeedback


async def add_rag_activity(
        chat_id: int,
        bot_msg_id: int,
        retriever_type: RetrieverType,
        date: datetime,
        query: str,
        history_rephrase_query: str,
        response: str
):
    """
    Логирование использования RAG-системы.

    :param chat_id:                 Id чата с пользователем.
    :param bot_msg_id:              Id сообщения от бота.
    :param retriever_type:          Тип ретривера.
    :param date:                    Дата+время ответа сообщения от бота.
    :param query:                   Запрос пользователя.
    :param history_rephrase_query:  Перефразированный на основе истории диалога с помощью GigaChat запрос пользователя.
    :param response:                Ответ ретривера (сообщение от бота).
    """
    stmt = insert(RAGUserFeedback).values(
        chat_id=chat_id,
        bot_msg_id=bot_msg_id,
        retriever_type=retriever_type.name,
        date=date.replace(tzinfo=None),
        query=query,
        history_rephrase_query=history_rephrase_query,
        response=response
    )
    async with async_session() as session:
        await session.execute(stmt)
        await session.commit()


async def update_rephrase_query(chat_id: int, bot_msg_id: int, response: str, rephrase_query: str = ''):
    """
    Обновление ответа относительно запроса, поступающего в RAG.

    :param chat_id:          Id чата с пользователем.
    :param bot_msg_id:       Id сообщения от бота.
    :param response:         Ответ ретривера (сообщение от бота).
    :param rephrase_query:   Перефразированный с помощью GigaChat запрос пользователя.
    """
    values = {'rephrase_query': rephrase_query} if rephrase_query else {}
    values['response'] = response

    stmt = (
        update(RAGUserFeedback).
        where(RAGUserFeedback.chat_id == chat_id, RAGUserFeedback.bot_msg_id == bot_msg_id).
        values(values)
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
