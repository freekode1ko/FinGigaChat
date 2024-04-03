from aiogram import F, Router, types
from aiogram.utils.chat_action import ChatActionMiddleware


router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(F.data.startswith('subscriptions_menu'))
async def subscriptions_menu(
        callback_query: types.CallbackQuery
) -> None:
    pass
