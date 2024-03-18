import copy

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder

from log.bot_logger import user_logger
from utils.base import user_in_whitelist
from utils.rag_router import RAGRouter
from configs.config import dict_of_emoji

router = Router()
router.message.middleware(ChatActionMiddleware())

emoji = copy.deepcopy(dict_of_emoji)


class RagState(StatesGroup):
    rag_mode = State()
    rag_query = State()


def generate_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text=emoji['like'], callback_data='like'))
    keyboard.add(types.InlineKeyboardButton(text=emoji['dislike'], callback_data='dislike'))

    return keyboard.as_markup()


@router.message(Command('knowledgebase'))
async def set_rag_mode(message: types.Message, state: FSMContext) -> None:
    """
    Переключение в режим общения с Вопросно-ответной системой (ВОС)

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        await state.set_state(RagState.rag_mode)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

        cancel_command = 'завершить'
        cancel_msg = f'Напишите «{cancel_command}» для завершения общения с Базой Знаний'
        msg_text = 'Начато общение с Базой Знаний\n\n' + cancel_msg

        buttons = [[types.KeyboardButton(text=cancel_command)]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True, input_field_placeholder=cancel_msg, one_time_keyboard=True
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
    """Отправка пользователю ответа, сформированного ВОС, на сообщение пользователя"""
    await ask_qa_system(message)


async def ask_qa_system(message: types.Message, first_user_query: str = '') -> None:
    """
    Отправляет ответ на запрос пользователя
    :param message: Message от пользователя
    :param first_user_query: запрос от пользователя вне режима ВОС
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    await message.bot.send_chat_action(message.chat.id, 'typing')
    query = first_user_query if first_user_query else user_msg
    rag_obj = RAGRouter(chat_id, full_name, query)
    response = rag_obj.get_response_from_rag()

    emoji_keyboard = generate_keyboard()
    await message.answer(response,  parse_mode='HTML', disable_web_page_preview=True, reply_markup=emoji_keyboard)


@router.callback_query(F.data.endswith('like'))
async def callback_keyboard(callback_query: types.CallbackQuery):

    mark = callback_query.data
    bot_msg = callback_query.message.text

    if mark == 'like':
        txt = 'Я рад, что вам понравилось!'
    else:
        txt = 'Я буду стараться лучше...'

    # обновление кнопки на одну не работающую
    button = [types.InlineKeyboardButton(text=txt, callback_data='none')]
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[button, ])
    await callback_query.message.edit_text(text=bot_msg, reply_markup=keyboard)
