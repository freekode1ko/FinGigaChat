from aiogram import F, Router, types
from aiogram.utils.chat_action import ChatActionMiddleware


router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(F.data.startswith('ai_menu'))
async def ai_menu(
        callback_query: types.CallbackQuery
) -> None:
    pass
