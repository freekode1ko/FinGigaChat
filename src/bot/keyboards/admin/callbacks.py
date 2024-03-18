from aiogram.filters.callback_data import CallbackData

from constants import admin as callback_prefixes


class DeleteMessageByType(CallbackData, prefix=callback_prefixes.DELETE_NEWSLETTER_MESSAGES_BY_TYPE):
    message_type_id: int


class ApproveDeleteMessageByType(CallbackData, prefix=callback_prefixes.APPROVE_DELETE_NEWSLETTER_MESSAGES_BY_TYPE):
    message_type_id: int
