"""Функции для обработки ответов от RAG."""
import textwrap

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from constants.constants import DEFAULT_RAG_ANSWER, TELEGRAM_MESSAGE_MAX_LEN
from constants.enums import RetrieverType
from constants.texts import texts_manager
from db.rag_user_feedback import add_rag_activity, update_response
from db.redis import user_dialog
from keyboards.rag.constructors import get_feedback_kb
from utils.base import clear_text_from_url
from utils.rag_utils.rag_router import RAGRouter


text_wrapper = textwrap.TextWrapper(
    width=TELEGRAM_MESSAGE_MAX_LEN - len(DEFAULT_RAG_ANSWER) - 2,  # 2 cимвола - \n\n
    placeholder='...',
    replace_whitespace=False,
    max_lines=1,
)


def format_response(answer: str) -> str:
    """Добавление футера к ответу от РАГ."""
    if answer != DEFAULT_RAG_ANSWER:
        answer = text_wrapper.wrap(answer)[0]  # FIXME: сделать по тз заказчика, когда оно появятся
        answer = texts_manager.RAG_FORMAT_ANSWER.format(answer=answer)
    return answer


async def get_response(
        chat_id: int,
        full_name: str,
        user_query: str,
        use_rephrase: bool,
        rephrase_query: str = '',
) -> tuple[RetrieverType, str, dict | None]:
    """
    Получение ответа от Базы Знаний или GigaChat.

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
    response = await rag_obj.get_response()
    if isinstance(response, str):
        return rag_obj.retriever_type, response, None
    return rag_obj.retriever_type, response['body'], response.get('metadata')


async def add_data_to_db(
        session: AsyncSession,
        msg: types.Message,
        user_query: str,
        clear_response: str,
        retriever_type: RetrieverType,
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
    :param retriever_type:  Тип ретривера (или GigaChat).
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
            retriever_type=retriever_type,
            date=msg.date,
            query=user_query,
            history_query=history_query,
            history_response=clear_response
        )
    else:
        await update_response(
            session=session,
            chat_id=msg.chat.id,
            bot_msg_id=msg.message_id,
            response=clear_response,
            rephrase_query=rephrase_query
        )

    # обновление истории диалога пользователя и ИИ
    await user_dialog.update_dialog(
        chat_id=msg.chat.id,
        msgs={'user': user_query, 'ai': clear_response},
        need_replace=need_replace
    )


async def update_keyboard_of_penultimate_bot_msg(message: types.Message, state: FSMContext) -> None:
    """Обновляет клавиатуру предпоследнего сообщения от рага: убирает кнопку генерации."""
    data = await state.get_data()
    if (rag_last_bot_msg := data.get('rag_last_bot_msg')) is not None:
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=rag_last_bot_msg,
                reply_markup=get_feedback_kb()
            )
        except TelegramBadRequest:
            pass
