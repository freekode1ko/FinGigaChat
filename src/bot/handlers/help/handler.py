from aiogram import F, Router, types
from aiogram.utils.chat_action import ChatActionMiddleware

from configs import config
from log.bot_logger import user_logger
from utils.base import user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(F.data.startswith('help'))
async def help_message(
        callback_query: types.CallbackQuery
) -> None:
    """
    Вывод сообщения с описанием бота и лицами для связи

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = 'help'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    if await user_in_whitelist(from_user.model_dump_json()):
        help_text = config.help_text
        to_pin = await callback_query.message.answer(help_text, protect_content=False)
        msg_id = to_pin.message_id
        await callback_query.bot.pin_chat_message(chat_id=chat_id, message_id=msg_id)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
