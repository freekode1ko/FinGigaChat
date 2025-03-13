"""Функции для обработки ответов от RAG."""
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from constants.enums import RetrieverType
from db.api.rag.rag_user_feedback import add_rag_activity, get_user_reaction, update_response
from db.redis import user_dialog
from keyboards.rag.constructors import get_feedback_kb
from log.bot_logger import logger
from utils.base import clear_text_from_url
from utils.rag_utils.rag_router import RagResponse, RAGRouter


async def query_rag(
        chat_id: int,
        full_name: str,
        user_query: str,
        use_rephrase: bool,
        rephrase_query: str = '',
) -> tuple[RetrieverType, RagResponse]:
    """
    Запрос к RAG: получение типа и ответа из Базы Знаний или GigaChat.

    :param chat_id:              Telegram id чата пользователя.
    :param full_name:            Полное имя пользователя.
    :param user_query:           Запрос пользователя.
    :param rephrase_query:       Перефразированный с помощью GigaChat запрос пользователя.
    :param use_rephrase:         Нужно ли использовать перефразированный запрос пользователя для получения ответа.
    :return:                     Тип ретривера или GigaChat, который ответил на запрос, и ответы на запрос
                                 (чистый (без футера) и отформатированный (с футером)).
    """
    rag_obj = RAGRouter(chat_id, full_name, user_query, rephrase_query, use_rephrase)
    await rag_obj.get_rag_type()
    try:
        response = await rag_obj.get_response()
    except Exception as exc:
        logger.exception(f'При получении ответа на вопрос "{user_query}": произошла ошибка {type(exc)}:{exc}')
        raise RuntimeError
    return rag_obj.retriever_type, response


async def add_data_to_db(
        session: AsyncSession,
        msg: types.Message,
        user_query: str,
        clear_response: str,
        rag_type: RetrieverType,
        history_query: str = '',
        rephrase_query: str = '',
        need_replace: bool = False
) -> None:
    """
    Добавление данных, связанных с RAG-сервисами, в БД.

    :param session:         Асинхронная сессия базы данных.
    :param msg:             Message от пользователя.
    :param user_query:      Запрос пользователя.
    :param clear_response:  Неотформатированный ответ на запрос.
    :param rag_type:        Тип rag (или GigaChat).
    :param history_query:   Перефразированный с помощью истории диалога запрос пользователя.
    :param rephrase_query:  Перефразированный запрос пользователя.
    :param need_replace:    Нужно ли изменять последние сообщения в диалоге.
    """
    clear_response = clear_text_from_url(clear_response)

    # сохранение пользовательской активности с ИИ
    if history_query:
        await add_rag_activity(
            session=session,
            chat_id=msg.chat.id,
            bot_msg_id=msg.message_id,
            retriever_type=rag_type,
            date=msg.date,
            query=user_query,
            history_query=history_query,
            history_response=clear_response
        )
    else:
        await update_response(
            session=session,
            chat_id=msg.chat.id,
            msg_id=msg.message_id,
            response=clear_response,
            rephrase_query=rephrase_query
        )

    # обновление истории диалога пользователя и ИИ
    await user_dialog.update_dialog(
        chat_id=msg.chat.id,
        msgs={'user': user_query, 'ai': clear_response},
        need_replace=need_replace
    )


async def update_keyboard_of_penultimate_bot_msg(session: AsyncSession, message: types.Message, state: FSMContext) -> None:
    """Обновляет клавиатуру предпоследнего сообщения от рага: убирает кнопку генерации."""
    data = await state.get_data()
    if not data.get('rag_user_msg'):
        return

    reaction = await get_user_reaction(session, message.chat.id, data['rag_user_msg'].message_id)
    if reaction is not None:
        return

    if rag_bot_msgs_ids := data.get('rag_bot_msgs_ids'):
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=rag_bot_msgs_ids[-1],
                reply_markup=get_feedback_kb(data['rag_user_msg'])
            )
        except TelegramBadRequest:
            pass
