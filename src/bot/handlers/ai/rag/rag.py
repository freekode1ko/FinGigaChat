"""Описание обработчиков событий при общении пользователя с RAG-системами."""
from aiogram import F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from constants.constants import DEFAULT_RAG_ANSWER, END_BUTTON_TXT
from constants.enums import FeatureType, RetrieverType
from constants.texts import texts_manager
from db.rag_user_feedback import add_rag_activity, update_response, update_user_reaction
from db.redis import del_dialog_and_history_query, get_history_query, get_last_user_msg, update_dialog, update_history_query
from handlers.ai.handler import router
from keyboards.analytics.constructors import get_few_full_research_kb
from keyboards.rag.callbacks import RegenerateResponse, GetReports
from keyboards.rag.constructors import get_feedback_kb, get_feedback_regenerate_kb
from log.bot_logger import user_logger
from utils.base import clear_text_from_url
from utils.decorators import has_access_to_feature
from utils.handler_utils import audio_to_text
from utils.rag_utils.rag_rephrase import get_rephrase_query, get_rephrase_query_by_history
from utils.rag_utils.rag_router import RAGRouter


class RagState(StatesGroup):
    """Автомат состояний общения с RAG-системами."""

    rag_mode = State()
    rag_query = State()
    rag_last_bot_msg = State()
    reports_data = State()


@router.message(F.text.lower().in_({'clear', 'очистить историю диалога', 'очистить историю'}))
@has_access_to_feature(FeatureType.knowledgebase, is_need_answer=False)
async def clear_user_dialog_if_need(message: types.Message, state: FSMContext) -> None:
    """
    Очистка пользовательской истории диалога, если завершается состояние RagState.

    :param message:     Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param state:       Состояние FSM.
    """
    state_name = await state.get_state()
    if state_name == RagState.rag_mode:
        await update_keyboard_of_penultimate_bot_msg(message, state)
        await del_dialog_and_history_query(message.from_user.id)
        await message.answer(texts_manager.RAG_CLEAR_HISTORY)


@router.message(Command('knowledgebase'))
@has_access_to_feature(FeatureType.knowledgebase)
async def set_rag_mode(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    """
    Переключение в режим общения с Вопросно-ответной системой (ВОС).

    :param message:     Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param state:       Состояние FSM.
    :param session:     Асинхронная сессия базы данных.
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    await state.set_state(RagState.rag_mode)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

    buttons = [
        [
            types.KeyboardButton(text='Очистить историю диалога'),
            types.KeyboardButton(text=END_BUTTON_TXT),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder=texts_manager.RAG_FINISH_STATE,
        one_time_keyboard=True
    )

    data = await state.get_data()
    first_user_query = data.get('rag_query', None)

    if first_user_query:
        await message.answer(texts_manager.RAG_FIRST_USER_QUERY.format(query=first_user_query), reply_markup=keyboard)
        await ask_with_dialog(message, state, session, first_user_query)
    else:
        await message.answer(texts_manager.RAG_START_STATE, reply_markup=keyboard)


@router.message(RagState.rag_mode)
async def handler_rag_mode(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Отправка пользователю ответа, сформированного ВОС, на сообщение пользователя.

    :param message:     Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param state:       Состояние FSM.
    :param session:     Асинхронная сессия базы данных.
    """
    if message.voice:
        user_msg = await audio_to_text(message)
    else:
        user_msg = message.text
    await ask_with_dialog(message, state, session, user_msg)


async def _get_response(
        chat_id: int,
        full_name: str,
        user_query: str,
        use_rephrase: bool,
        rephrase_query: str = '',
) -> tuple[RetrieverType, str, dict | None]:
    """
    Получение ответа от Базы Знаний или GigaChat.

    :param chat_id:              Telegram id пользователя.
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


def format_response(answer: str) -> str:
    """Добавление футера к ответу от РАГ."""
    if answer != DEFAULT_RAG_ANSWER:
        answer = texts_manager.RAG_FORMAT_ANSWER.format(answer=answer)
    return answer


async def _add_data_to_db(
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
    await update_dialog(
        user_id=msg.chat.id,
        msgs={'user': user_query, 'ai': clear_response},
        need_replace=need_replace
    )


async def ask_with_dialog(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession,
        first_user_query: str = '',
) -> None:
    """
    Отправляет ответ на запрос пользователя, используя историю диалога.

    :param state:              Состояние.
    :param message:            Message от пользователя.
    :param session:            Асинхронная сессия базы данных.
    :param first_user_query:   Запрос от пользователя вне режима ВОС.
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    await update_keyboard_of_penultimate_bot_msg(message, state)

    async with ChatActionSender(bot=message.bot, chat_id=chat_id):
        user_query = first_user_query if first_user_query else user_msg
        history_query = await get_rephrase_query_by_history(chat_id, full_name, user_query)
        result = await _get_response(chat_id, full_name, user_query, True, history_query)
        retriever_type, response, metadata = result
        reports_data = metadata.get('reports_data') if metadata else None

        msg = await message.answer(
            text=format_response(response),
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=get_feedback_regenerate_kb(rephrase_query=True, with_reports=reports_data is not None)
        )

        await _add_data_to_db(
            session=session,
            msg=msg,
            user_query=user_query,
            clear_response=response,
            retriever_type=retriever_type,
            history_query=history_query
        )

        await update_history_query(chat_id, history_query)
        await state.update_data(rag_last_bot_msg=msg.message_id, reports_data=reports_data)


@router.callback_query(RegenerateResponse.filter())
@has_access_to_feature(FeatureType.knowledgebase)
async def ask_without_dialog(
        call: types.CallbackQuery,
        callback_data: RegenerateResponse,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    """
    Отправляет ответ на запрос пользователя без использования истории диалога.

    :param call:              Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:     Объект, содержащий дополнительную информацию.
    :param state:             Состояние FSM.
    :param session:           Асинхронная сессия базы данных.
    """
    async with ChatActionSender(bot=call.bot, chat_id=call.message.chat.id):
        chat_id = call.message.chat.id
        full_name = call.message.from_user.full_name
        user_query = await get_last_user_msg(chat_id)
        if not user_query:
            await update_keyboard_of_penultimate_bot_msg(call.message, state)
            await call.bot.send_message(chat_id, texts_manager.RAG_TRY_AGAIN)

        if callback_data.rephrase_query:
            history_query = await get_history_query(chat_id)
            rephrase_query = await get_rephrase_query(chat_id, full_name, user_query, history_query)
            result = await _get_response(chat_id, full_name, user_query, True, rephrase_query)
        else:
            rephrase_query = ''
            result = await _get_response(chat_id, full_name, user_query, use_rephrase=False)

        retriever_type, response, metadata = result
        reports_data = metadata.get('reports_data') if metadata else None
        with_reports = reports_data is not None
        if rephrase_query:
            kb = get_feedback_regenerate_kb(initially_query=True, with_reports=with_reports)
        else:
            kb = get_feedback_kb(with_reports=with_reports)

        msg = await call.message.edit_text(
            text=format_response(response),
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=kb
        )

        await _add_data_to_db(
            session,
            msg,
            user_query,
            response,
            retriever_type,
            rephrase_query=rephrase_query,
            need_replace=True
        )

        await state.update_data(rag_last_bot_msg=msg.message_id, reports_data=reports_data)


@router.callback_query(F.data.endswith('like'))
@has_access_to_feature(FeatureType.knowledgebase)
async def callback_keyboard(callback_query: types.CallbackQuery, session: AsyncSession) -> None:
    """Обработка обратной связи от пользователя."""
    if callback_query.data == 'like':
        txt, reaction = texts_manager.RAG_LIKE_FEEDBACK, True
    else:
        txt, reaction = texts_manager.RAG_DISLIKE_FEEDBACK, False

    # обновление кнопки на одну не работающую
    button = [types.InlineKeyboardButton(text=txt, callback_data='none')]
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[button, ])
    await callback_query.message.edit_text(text=callback_query.message.text, reply_markup=keyboard,
                                           disable_web_page_preview=True, parse_mode='HTML')

    # добавим в бд обратную связь от пользователя
    await update_user_reaction(session, callback_query.message.chat.id, callback_query.message.message_id, reaction)


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


@router.callback_query(GetReports.filter())
async def get_full_version_of_research(
        callback_query: types.CallbackQuery,
        callback_data: GetReports,
        state: FSMContext,
) -> None:
    """
    Получить полную версию отчета

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:   Содержит дополнительную информацию по отчету.
    :param state:           Состояние, в котором находится пользователь.
    """
    kb = InlineKeyboardBuilder()
    buttons = callback_query.message.reply_markup.inline_keyboard[0]  # берем первую строчку из существующей клавиатуры
    for b in buttons:
        kb.add(types.InlineKeyboardButton(text=b.text, callback_data=b.callback_data))

    data = await state.get_data()
    reports_data = data.get('reports_data')
    kb = get_few_full_research_kb(kb, reports_data)

    try:
        await callback_query.message.edit_text(
            text=callback_query.message.text, reply_markup=kb, disable_web_page_preview=True, parse_mode='HTML'
        )
    except TelegramBadRequest:
        pass
    user_logger.info(f'*{callback_query.message.chat.id}* {callback_query.from_user.full_name} - {callback_data.pack()}')
