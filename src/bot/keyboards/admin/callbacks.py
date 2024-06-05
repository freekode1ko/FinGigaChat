"""CallbackData для администрирования"""
from aiogram.filters.callback_data import CallbackData

from constants import admin as callback_prefixes


class DeleteMessageByType(CallbackData, prefix=callback_prefixes.DELETE_NEWSLETTER_MESSAGES_BY_TYPE):
    """CallbackData удаления сообщения по типу"""

    message_type_id: int


class ApproveDeleteMessageByType(CallbackData, prefix=callback_prefixes.APPROVE_DELETE_NEWSLETTER_MESSAGES_BY_TYPE):
    """CallbackData для подтверждения удаления сообщения по типу"""

    message_type_id: int
