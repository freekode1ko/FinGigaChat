"""Описание обработчиков событий при общении пользователя с RAG-системами."""
from aiogram import F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from constants.constants import DISLIKE_FEEDBACK, LIKE_FEEDBACK
from constants.enums import RetrieverType
from db.api.user_dialog_history import user_dialog_history_db
from db.rag_user_feedback import add_rag_activity, update_user_reaction
from handlers.ai.handler import router
from keyboards.rag.callbacks import RegenerateResponse
from keyboards.rag.constructors import get_feedback_regenerate_kb, get_feedback_kb
from log.bot_logger import user_logger
from utils.base import user_in_whitelist
from utils.rag_utils.rag_dialog import get_rephrase_query
from utils.rag_utils.rag_router import RAGRouter


class RagState(StatesGroup):
    """Автомат состояний общения с RAG-системами."""

    rag_mode = State()
    rag_query = State()


async def clear_user_dialog_if_need(message: types.Message, state: FSMContext) -> None:
    """Очистка пользовательской истории диалога, если завершается состояние RagState."""
    state_name = await state.get_state()
    if state_name == RagState.rag_mode:
        await user_dialog_history_db.clear_user_dialog(message.from_user.id)
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
            await ask_qa_system(message, first_user_query)
        else:
            await message.answer(msg_text, reply_markup=keyboard)

    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.message(RagState.rag_mode)
async def handler_rag_mode(message: types.Message) -> None:
    """Отправка пользователю ответа, сформированного ВОС, на сообщение пользователя."""
    await ask_qa_system(message)


async def _get_response(
        chat_id: int,
        full_name: str,
        user_query: str,
        use_rephrase: bool,
        rephrase_query: str = ''
) -> tuple[RetrieverType, str]:
    """
    Получение ответа от Базы Знаний или GigaChat.

    :param chat_id:              Telegram id пользователя.
    :param full_name:            Полное имя пользователя.
    :param user_query:           Запрос пользователя.
    :param rephrase_query:       Перефразированный с помощью GigaChat запрос пользователя.
    :param use_rephrase:         Нужно ли использовать перефразированный запрос пользователя для получения ответа.
    :return:                     Тип ретривера или GigaChat, который ответил на запрос, и ответ на запрос.
    """
    rag_obj = RAGRouter(chat_id, full_name, user_query, rephrase_query, use_rephrase)
    response = rag_obj.get_response_from_rag()
    return rag_obj.retriever_type, response


async def _add_data_to_db(
        msg: types.Message,
        user_query: str,
        response: str,
        retriever_type: RetrieverType,
        rephrase_query: str = ''
) -> None:
    """
    Добавление данных, связанных с RAG-сервисами, в БД.

    :param msg:             Message от пользователя.
    :param user_query:      Запрос пользователя.
    :param response:        Ответ на запрос пользователя.
    :param retriever_type:  Тип ретривера (или GigaChat).
    :param rephrase_query:  Перефразированный на основе истории диалога вопрос пользователя.
    """
    # сохранение пользовательской активности с ИИ
    await add_rag_activity(
        chat_id=msg.chat.id,
        bot_msg_id=msg.message_id,
        date=msg.date,
        query=user_query,
        rephrase_query=rephrase_query,
        response=response,
        retriever_type=retriever_type
    )

    # обновление истории диалога пользователя и ИИ
    await user_dialog_history_db.add_msgs_to_user_dialog(
        user_id=msg.chat.id,
        messages={'user': user_query, 'ai': response},
        need_replace=rephrase_query == ''
    )


async def ask_qa_system(message: types.Message, first_user_query: str = '') -> None:
    """
    Отправляет ответ на запрос пользователя.

    :param message:            Message от пользователя.
    :param first_user_query:   Запрос от пользователя вне режима ВОС.
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    await message.bot.send_chat_action(chat_id, 'typing')

    user_query = first_user_query if first_user_query else user_msg
    rephrase_query = await get_rephrase_query(chat_id, full_name, user_query)

    retriever_type, response = await _get_response(chat_id, full_name, user_query, True, rephrase_query)

    msg = await message.answer(
        text=response,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=get_feedback_regenerate_kb()
    )

    await _add_data_to_db(msg, user_query, response, retriever_type, rephrase_query)


@router.callback_query(RegenerateResponse.filter())
async def regenerate_callback(call: types.CallbackQuery) -> None:
    """

    """
    chat_id = call.message.chat.id
    full_name = call.message.from_user.full_name
    user_query = await user_dialog_history_db.get_last_user_query(chat_id)
    await call.message.bot.send_chat_action(chat_id, 'typing')

    retriever_type, response = await _get_response(chat_id, full_name, user_query, use_rephrase=False)

    msg = await call.message.edit_text(
        text=response,
        parse_mode='HTML',
        disable_web_page_preview=True,
        reply_markup=get_feedback_kb()
    )

    await _add_data_to_db(msg, user_query, response, retriever_type)


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
