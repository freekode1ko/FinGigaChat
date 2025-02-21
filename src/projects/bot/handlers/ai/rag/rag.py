"""Описание обработчиков событий при общении пользователя с RAG-системами."""
import asyncio

from aiogram import Bot, F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from constants.constants import DEFAULT_RAG_ANSWER, END_BUTTON_TXT
from constants.enums import FeatureType
from constants.texts import texts_manager
from db.rag_user_feedback import update_user_reaction
from db.redis import user_constants, user_dialog
from handlers.ai.handler import router
from handlers.ai.rag.utils import add_data_to_db, query_rag, update_keyboard_of_penultimate_bot_msg
from keyboards.analytics.constructors import get_few_full_research_kb
from keyboards.rag.callbacks import GetReports, RegenerateResponse, SetReaction
from keyboards.rag.constructors import get_feedback_kb, get_feedback_regenerate_kb
from log.bot_logger import logger, user_logger
from utils.decorators import has_access_to_feature
from utils.handler_utils import audio_to_text
from utils.rag_utils.rag_rephrase import get_rephrase_query, get_rephrase_query_by_history


class RagState(StatesGroup):
    """Автомат состояний общения с RAG-системами."""

    rag_mode = State()
    reports_data = State()
    rag_user_msg = State()
    rag_bot_msgs_ids = State()


@router.message(F.text.lower().in_({'clear', 'очистить историю диалога', 'очистить историю'}))
@has_access_to_feature(FeatureType.knowledgebase, is_need_answer=False)
async def clear_user_dialog_if_need(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Очистка пользовательской истории диалога, если завершается состояние RagState.

    :param message:     Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param state:       Состояние FSM.
    """
    state_name = await state.get_state()
    if state_name == RagState.rag_mode:
        await update_keyboard_of_penultimate_bot_msg(session, message, state)
        await user_dialog.del_dialog_and_history_query(message.chat.id)
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
    await state.set_state(RagState.rag_mode)
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
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
    await message.answer(texts_manager.RAG_START_STATE, reply_markup=keyboard)

    state_data = await state.get_data()
    first_rag_user_msg: types.Message | None = state_data.get('rag_user_msg')
    if first_rag_user_msg:
        waiting_answer_msg = await message.answer(texts_manager.RAG_WAITING_ANSWER.format(query=first_rag_user_msg.text))
        asyncio.create_task(
            ask_with_dialog(message, state, session, waiting_answer_msg, first_rag_user_msg.text),
            name=f'{user_constants.BACKGROUND_TASK_NAME}{chat_id}'
        )


@router.message(RagState.rag_mode)
async def handler_rag_mode(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Отправка пользователю ответа, сформированного ВОС, на сообщение пользователя.

    :param message:     Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param state:       Состояние FSM.
    :param session:     Асинхронная сессия базы данных.
    """
    user_msg = await audio_to_text(message) if message.voice else message.text
    waiting_answer_msg = await message.answer(texts_manager.RAG_WAITING_ANSWER.format(query=user_msg))

    state_data = await state.get_data()
    if state_data.get('rag_user_msg'):
        await update_keyboard_of_penultimate_bot_msg(session, message, state)
    await state.update_data(rag_user_msg=message)
    asyncio.create_task(
        ask_with_dialog(message, state, session, waiting_answer_msg, user_msg),
        name=f'{user_constants.BACKGROUND_TASK_NAME}{message.chat.id}'
    )


async def ask_with_dialog(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession,
        waiting_answer_msg: types.Message,
        first_user_query: str = '',
) -> None:
    """
    Отправляет ответ на запрос пользователя, используя историю диалога.

    :param state:              Состояние.
    :param message:            Message от пользователя.
    :param session:            Асинхронная сессия базы данных.
    :param waiting_answer_msg: Сообщение от бота с процессом формирования ответа.
    :param first_user_query:   Запрос от пользователя вне режима ВОС.
    """
    user_query = first_user_query or message.text
    chat_id, full_name = message.chat.id, message.from_user.full_name
    await user_constants.update_user_constant(user_constants.BACKGROUND_TASK_NAME, chat_id, user_query)

    try:
        async with ChatActionSender(bot=message.bot, chat_id=chat_id):

            state_data = await state.get_data()
            history_query = await get_rephrase_query_by_history(chat_id, full_name, user_query)

            rag_type, response = await query_rag(chat_id, full_name, user_query, True, history_query)
            reports_data = response.metadata.get('reports_data_research')

            kb = get_feedback_regenerate_kb(
                user_msg=state_data['rag_user_msg'],
                rephrase_query=True,
                with_reports=reports_data is not None
            )
            msgs_ids = await send_rag_messages(message.bot, chat_id, response.answers, kb)

            await add_data_to_db(
                session=session,
                msg=state_data['rag_user_msg'],
                user_query=user_query,
                clear_response='\n'.join(response.answers),
                rag_type=rag_type,
                history_query=history_query
            )
            await state.update_data(rag_bot_msgs_ids=msgs_ids, reports_data=reports_data)
            await user_dialog.update_history_query(chat_id, history_query)
            await user_constants.del_user_constant(user_constants.BACKGROUND_TASK_NAME, chat_id)
            await waiting_answer_msg.delete()

    except (TelegramBadRequest, asyncio.TimeoutError, RuntimeError) as e:
        await waiting_answer_msg.edit_text(texts_manager.RAG_ERROR_ANSWER + '\n' + texts_manager.RAG_TRY_AGAIN)
        logger.error(f'Ошибка при получении ответа от ВОС: {type(e)}: {e}')
        # в finally не стоит переносить, так как он и при перезапуске бота удаляет константу,
        # а она нужна для просьбы повторного запроса
        await user_constants.del_user_constant(user_constants.BACKGROUND_TASK_NAME, chat_id)


async def ask_without_dialog(
        call: types.CallbackQuery,
        callback_data: RegenerateResponse,
        state: FSMContext,
        session: AsyncSession,
        user_query: str
) -> None:
    """
    Отправляет ответ на запрос пользователя без использования истории диалога.

    :param call:              Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:     Объект, содержащий дополнительную информацию.
    :param state:             Состояние FSM.
    :param session:           Асинхронная сессия базы данных.
    :param user_query:        Пользовательский вопрос к РАГ.
    """
    # call.message.from_user.id != chat_id, но в бд хранится user_id равный chat_id
    chat_id, full_name = call.message.chat.id, call.message.from_user.full_name

    await delete_rag_messages(call.bot, chat_id, state)
    await user_constants.update_user_constant(user_constants.BACKGROUND_TASK_NAME, chat_id, user_query)
    waiting_answer_msg = await call.bot.send_message(chat_id, texts_manager.RAG_WAITING_ANSWER.format(query=user_query))

    try:
        async with ChatActionSender(bot=call.bot, chat_id=call.message.chat.id):
            if callback_data.need_rephrase_query:
                history_query = await user_dialog.get_history_query(chat_id)
                rephrase_query = await get_rephrase_query(chat_id, full_name, user_query, history_query)
                rag_type, response = await query_rag(chat_id, full_name, user_query, True, rephrase_query)
            else:
                rephrase_query = ''
                rag_type, response = await query_rag(chat_id, full_name, user_query, use_rephrase=False)

            reports_data = response.metadata.get('reports_data_research')
            with_reports = reports_data is not None
            state_data = await state.get_data()
            if rephrase_query:
                kb = get_feedback_regenerate_kb(
                    user_msg=state_data['rag_user_msg'],
                    initially_query=True,
                    with_reports=with_reports
                )
            else:
                kb = get_feedback_kb(
                    user_msg=state_data['rag_user_msg'],
                    with_reports=with_reports
                )

            msgs_ids = await send_rag_messages(call.bot, chat_id, response.answers, kb)

            await add_data_to_db(
                session=session,
                msg=state_data['rag_user_msg'],
                user_query=user_query,
                clear_response='\n'.join(response.answers),
                rag_type=rag_type,
                rephrase_query=rephrase_query,
                need_replace=True
            )
            await state.update_data(
                reports_data=reports_data,
                rag_bot_msgs_ids=msgs_ids if callback_data.need_rephrase_query else []
            )
            await user_constants.del_user_constant(user_constants.BACKGROUND_TASK_NAME, chat_id)
            await waiting_answer_msg.delete()

    except (TelegramBadRequest, asyncio.TimeoutError, RuntimeError) as e:
        await call.message.edit_text(texts_manager.RAG_ERROR_ANSWER + '\n' + texts_manager.RAG_TRY_AGAIN)
        logger.error(f'Ошибка при получении ответа от ВОС: {type(e)}: {e}')
        # в finally не стоит переносить, так как он и при перезапуске бота удаляет константу,
        # а она нужна для просьбы повторного запроса
        await user_constants.del_user_constant(user_constants.BACKGROUND_TASK_NAME, chat_id)


@router.callback_query(RegenerateResponse.filter())
@has_access_to_feature(FeatureType.knowledgebase)
async def ask_regenerate(
        call: types.CallbackQuery,
        callback_data: RegenerateResponse,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    """
    Отправляет ответ на запрос пользователя по кнопке перегенерации.

    :param call:              Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:     Объект, содержащий дополнительную информацию.
    :param state:             Состояние FSM.
    :param session:           Асинхронная сессия базы данных.
    """
    chat_id = call.message.chat.id  # call.message.from_user.id != chat_id, но в бд хранится user_id равный chat_id
    user_query = await user_dialog.get_last_user_msg(chat_id)
    state_data = await state.get_data()
    if not user_query or not state_data.get('rag_user_msg'):
        await update_keyboard_of_penultimate_bot_msg(session, call.message, state)
        await call.bot.send_message(chat_id, texts_manager.RAG_TRY_AGAIN)
        return

    asyncio.create_task(
        ask_without_dialog(call, callback_data, state, session, user_query),
        name=f'{user_constants.BACKGROUND_TASK_NAME}{chat_id}'
    )


@router.callback_query(SetReaction.filter())
@has_access_to_feature(FeatureType.knowledgebase)
async def callback_keyboard(callback_query: types.CallbackQuery, callback_data: SetReaction, session: AsyncSession) -> None:
    """Обработка обратной связи от пользователя."""
    if callback_data.reaction == 'like':
        txt, reaction = texts_manager.RAG_LIKE_FEEDBACK, True
    else:
        txt, reaction = texts_manager.RAG_DISLIKE_FEEDBACK, False

    # обновление кнопки на одну не работающую
    button = [types.InlineKeyboardButton(text=txt, callback_data='none')]
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[button, ])
    await callback_query.message.edit_reply_markup(
        text=callback_query.message.message_id,
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode='HTML'
    )

    # добавим в бд обратную связь от пользователя
    await update_user_reaction(session, callback_query.message.chat.id, callback_data.user_msg_id, reaction)


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
        await callback_query.message.edit_reply_markup(
            text=callback_query.message.message_id, reply_markup=kb, disable_web_page_preview=True, parse_mode='HTML'
        )
    except TelegramBadRequest:
        pass
    user_logger.info(f'*{callback_query.message.chat.id}* {callback_query.from_user.full_name} - {callback_data.pack()}')


async def delete_rag_messages(bot: Bot, chat_id: int, state: FSMContext):
    """Удаление сообщений от РАГа."""
    data = await state.get_data()
    msgs_ids = data.get('rag_bot_msgs_ids', [])
    for msg_id in msgs_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except TelegramBadRequest:
            logger.exception(f'Ошибка удаления сообщения {msg_id} у пользователя {chat_id}')
            pass


async def send_rag_messages(bot: Bot, chat_id: int, answers: list[str], kb: types.InlineKeyboardMarkup) -> list[int]:
    """Отправка сообщений с ответами от РАГ."""
    msgs_ids = []
    last_index = len(answers) - 1
    for i, answer in enumerate(answers):

        if i == last_index and answer != DEFAULT_RAG_ANSWER:
            answer = texts_manager.RAG_FORMAT_ANSWER.format(answer=answer)

        msg = await bot.send_message(
            chat_id,
            text=answer,
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=kb if i == last_index else None
        )
        msgs_ids.append(msg.message_id)
    return msgs_ids
