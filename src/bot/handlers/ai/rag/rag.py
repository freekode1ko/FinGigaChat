"""Описание обработчиков событий при общении пользователя с RAG-системами."""
from aiogram import F, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionSender

from constants.constants import DISLIKE_FEEDBACK, LIKE_FEEDBACK
from constants.enums import RetrieverType
from db.rag_user_feedback import add_rag_activity, update_response, update_user_reaction
from db.redis import del_dialog, get_last_user_msg, update_dialog
from handlers.ai.handler import router
from keyboards.rag.callbacks import RegenerateResponse
from keyboards.rag.constructors import get_feedback_regenerate_kb, get_feedback_kb
from log.bot_logger import user_logger
from utils.base import clear_text_from_url, user_in_whitelist
from utils.rag_utils.rag_rephrase import get_rephrase_query, get_rephrase_query_by_history
from utils.rag_utils.rag_router import RAGRouter


class RagState(StatesGroup):
    """Автомат состояний общения с RAG-системами."""

    rag_mode = State()
    rag_query = State()
    rag_last_bot_msg = State()


async def clear_user_dialog_if_need(message: types.Message, state: FSMContext) -> None:
    """Очистка пользовательской истории диалога, если завершается состояние RagState."""
    state_name = await state.get_state()
    if state_name == RagState.rag_mode:
        await del_dialog(message.from_user.id)
        await update_keyboard_of_penultimate_bot_msg(message, state)
        await message.answer('История диалога очищена!')


@router.message(F.text.lower().in_({'clear', 'очистить историю диалога', 'очистить историю'}))
async def clear_user_dialog_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик отчистки истории диалога."""
    await clear_user_dialog_if_need(message, state)


@router.message(Command('knowledgebase'))
async def set_rag_mode(message: types.Message, state: FSMContext) -> None:
    """Переключение в режим общения с Вопросно-ответной системой (ВОС)."""
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        await state.set_state(RagState.rag_mode)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

        cancel_command = 'Завершить'
        cancel_msg = f'Напишите «{cancel_command}» для завершения общения с Базой Знаний'
        msg_text = 'Начато общение с Базой Знаний\n\n' + cancel_msg

        buttons = [
            [
                types.KeyboardButton(text='Очистить историю диалога'),
                types.KeyboardButton(text=cancel_command),
            ]
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True,
            input_field_placeholder=cancel_msg,
            one_time_keyboard=True
        )

        data = await state.get_data()
        first_user_query = data.get('rag_query', None)

        if first_user_query:
            await message.answer(f'Подождите...\nФормирую ответ на запрос: "{first_user_query}"\n{cancel_msg}',
                                 reply_markup=keyboard)
            await ask_with_dialog(message, state, first_user_query)
        else:
            await message.answer(msg_text, reply_markup=keyboard)

    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.message(RagState.rag_mode)
async def handler_rag_mode(message: types.Message, state: FSMContext) -> None:
    """Отправка пользователю ответа, сформированного ВОС, на сообщение пользователя."""
    await ask_with_dialog(message, state)


async def _get_response(
        chat_id: int,
        full_name: str,
        user_query: str,
        use_rephrase: bool,
        rephrase_query: str = ''
) -> tuple[RetrieverType, str, str]:
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
    clear_response, format_response = await rag_obj.get_response()
    return rag_obj.retriever_type, clear_response, format_response


async def _add_data_to_db(
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
            chat_id=msg.chat.id,
            bot_msg_id=msg.message_id,
            date=msg.date,
            query=user_query,
            history_query=history_query,
            history_response=clear_response,
            retriever_type=retriever_type
        )
    else:
        await update_response(
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


async def ask_with_dialog(message: types.Message, state: FSMContext, first_user_query: str = '') -> None:
    """
    Отправляет ответ на запрос пользователя, используя историю диалога.

    :param state:              Состояние.
    :param message:            Message от пользователя.
    :param first_user_query:   Запрос от пользователя вне режима ВОС.
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    async with ChatActionSender(bot=message.bot, chat_id=chat_id):
        user_query = first_user_query if first_user_query else user_msg
        history_query = await get_rephrase_query_by_history(chat_id, full_name, user_query)
        result = await _get_response(chat_id, full_name, user_query, True, history_query)
        retriever_type, clear_response, response = result

        msg = await message.answer(
            text=response,
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=get_feedback_regenerate_kb(rephrase_query=True)
        )

        await _add_data_to_db(
            msg,
            user_query,
            clear_response,
            retriever_type,
            history_query=history_query
        )

        await update_keyboard_of_penultimate_bot_msg(message, state)
        await state.update_data(rag_last_bot_msg=msg.message_id)


@router.callback_query(RegenerateResponse.filter())
async def ask_without_dialog(call: types.CallbackQuery, callback_data: RegenerateResponse, state: FSMContext) -> None:
    """Отправляет ответ на запрос пользователя без использования истории диалога."""
    async with ChatActionSender(bot=call.bot, chat_id=call.message.chat.id):
        chat_id = call.message.chat.id
        full_name = call.message.from_user.full_name
        user_query = await get_last_user_msg(chat_id)
        if not user_query:
            await update_keyboard_of_penultimate_bot_msg(call.message, state)
            await call.bot.send_message(chat_id, 'Напишите, пожалуйста, свой запрос еще раз')

        if callback_data.rephrase_query:
            rephrase_query = await get_rephrase_query(chat_id, full_name, user_query)
            result = await _get_response(chat_id, full_name, rephrase_query, use_rephrase=False)
            kb = get_feedback_regenerate_kb(initially_query=True)
        else:
            rephrase_query = ''
            result = await _get_response(chat_id, full_name, user_query, use_rephrase=False)
            kb = get_feedback_kb()

        retriever_type, clear_response, response = result

        msg = await call.message.edit_text(
            text=response,
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=kb
        )

        await _add_data_to_db(
            msg,
            user_query,
            clear_response,
            retriever_type,
            rephrase_query=rephrase_query,
            need_replace=True
        )

        await state.update_data(rag_last_bot_msg=msg.message_id)


@router.callback_query(F.data.endswith('like'))
async def callback_keyboard(callback_query: types.CallbackQuery) -> None:
    """Обработка обратной связи от пользователя."""
    if callback_query.data == 'like':
        txt, reaction = LIKE_FEEDBACK, True
    else:
        txt, reaction = DISLIKE_FEEDBACK, False

    # обновление кнопки на одну не работающую
    button = [types.InlineKeyboardButton(text=txt, callback_data='none')]
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[button, ])
    await callback_query.message.edit_text(text=callback_query.message.text, reply_markup=keyboard,
                                           disable_web_page_preview=True, parse_mode='HTML')

    # добавим в бд обратную связь от пользователя
    await update_user_reaction(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        reaction
    )


async def update_keyboard_of_penultimate_bot_msg(message: types.Message, state: FSMContext) -> None:
    """Обновляет клавиатуру предпоследнего сообщения от рага: убирает кнопку генерации."""
    data = await state.get_data()
    if (rag_last_bot_msg := data.get('rag_last_bot_msg', None)) is not None:
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=rag_last_bot_msg,
                reply_markup=get_feedback_kb()
            )
        except TelegramBadRequest:
            pass
