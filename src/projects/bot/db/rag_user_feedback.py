"""Методы по взаимодействию с таблицей UserRagFeedback в БД."""
import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from constants.enums import RetrieverType
from db.models import RAGUserFeedback


async def add_rag_activity(
        session: AsyncSession,
        chat_id: int,
        bot_msg_id: int,
        retriever_type: RetrieverType,
        date: datetime,
        query: str,
        history_query: str,
        history_response: str
) -> None:
    """
    Логирование использования RAG-системы.

    :param session:                 Асинхронная сессия базы данных.
    :param chat_id:                 Id чата с пользователем.
    :param bot_msg_id:              Id сообщения от бота.
    :param retriever_type:          Тип ретривера.
    :param date:                    Дата+время ответа сообщения от бота.
    :param query:                   Запрос пользователя.
    :param history_query:           Перефразированный на основе истории диалога с помощью GigaChat запрос пользователя.
    :param history_response:        Ответ ретривера (сообщение от бота).
    """
    stmt = insert(RAGUserFeedback).values(
        chat_id=chat_id,
        bot_msg_id=bot_msg_id,
        retriever_type=retriever_type.name,
        date=date.replace(tzinfo=None),
        query=query,
        history_query=history_query,
        history_response=history_response
    )
    await session.execute(stmt)
    await session.commit()


async def update_response(
        session: AsyncSession,
        chat_id: int,
        msg_id: int,
        response: str,
        rephrase_query: str = ''
) -> None:
    """
    Обновление ответа относительно запроса, поступающего в RAG.

    :param session:          Асинхронная сессия базы данных.
    :param chat_id:          Id чата с пользователем.
    :param msg_id:       Id сообщения от бота.
    :param response:         Ответ ретривера (сообщение от бота).
    :param rephrase_query:   Перефразированный с помощью GigaChat запрос пользователя.
    """
    if rephrase_query:
        values = {'rephrase_query': rephrase_query, 'rephrase_response': response}
    else:
        values = {'response': response}

    stmt = (
        update(RAGUserFeedback).
        where(RAGUserFeedback.chat_id == chat_id, RAGUserFeedback.bot_msg_id == msg_id).
        values(values)
    )
    await session.execute(stmt)
    await session.commit()


async def update_user_reaction(session: AsyncSession, chat_id: int, msg_id: int, reaction: bool) -> None:
    """
    Добавление обратной связи от пользователя по использованию RAG-системы.

    :param session:     Асинхронная сессия базы данных.
    :param chat_id:     Id чата с пользователем.
    :param msg_id:  Id сообщения с вопросом от пользователя.
    :param reaction:    Реакция пользователя на ответ RAG-системы (True/False).
    """
    stmt = (
        update(RAGUserFeedback)
        .where(RAGUserFeedback.chat_id == chat_id, RAGUserFeedback.bot_msg_id == msg_id)
        .values(reaction=reaction)
    )
    await session.execute(stmt)
    await session.commit()


async def get_user_reaction(session: AsyncSession, chat_id: int, msg_id: int) -> bool | None:
    """
    Получение обратной связи от пользователя по использованию RAG-системы.

    :param session:     Асинхронная сессия базы данных.
    :param chat_id:     Id чата с пользователем.
    :param msg_id:  Id сообщения с вопросом от пользователя.
    :return:            Значение реакции пользователя на ответ от РАГ.
    """
    stmt = (
        select(RAGUserFeedback.reaction)
        .where(RAGUserFeedback.chat_id == chat_id, RAGUserFeedback.bot_msg_id == msg_id)
    )
    return await session.scalar(stmt)
