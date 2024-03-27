import datetime

from sqlalchemy import text

from db.database import engine
from constants.enums import RetrieverType


def add_rag_activity(chat_id: int,
                     bot_msg_id: int,
                     retriever_type: RetrieverType,
                     date: datetime,
                     query: str,
                     response: str):
    """Логирование использования RAG-системы"""
    sql_query = text(
        'INSERT INTO rag_user_feedback (chat_id, bot_msg_id, retriever_type, date, query, response) '
        'VALUES (:chat_id, :bot_msg_id, :retriever_type, :date, :query, :response)'
    )
    with engine.connect() as conn:
        conn.execute(sql_query.bindparams(chat_id=chat_id,
                                          bot_msg_id=bot_msg_id,
                                          retriever_type=retriever_type.name,
                                          date=date,
                                          query=query,
                                          response=response))
        conn.commit()


def update_user_reaction(chat_id: int, bot_msg_id: int, reaction: bool):
    """Добавление обратной связи от пользователя по использованию RAG-системы"""
    sql_query = text('UPDATE rag_user_feedback SET reaction=:reaction WHERE chat_id=:chat_id AND bot_msg_id=:bot_msg_id')
    with engine.connect() as conn:
        conn.execute(sql_query.bindparams(chat_id=chat_id,
                                          bot_msg_id=bot_msg_id,
                                          reaction=reaction))
        conn.commit()
