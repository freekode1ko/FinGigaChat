from aiogram import Router
from aiogram.utils.chat_action import ChatActionMiddleware


router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'
