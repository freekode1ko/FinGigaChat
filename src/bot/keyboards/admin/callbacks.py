from aiogram.filters.callback_data import CallbackData

from constants.admin import DELETE_NEWSLETTER_MESSAGES_BY_TYPE, APPROVE_DELETE_NEWSLETTER_MESSAGES_BY_TYPE


class DeleteMessageByType(CallbackData, prefix=DELETE_NEWSLETTER_MESSAGES_BY_TYPE):
    message_type_id: int


class ApproveDeleteMessageByType(CallbackData, prefix=APPROVE_DELETE_NEWSLETTER_MESSAGES_BY_TYPE):
    message_type_id: int
