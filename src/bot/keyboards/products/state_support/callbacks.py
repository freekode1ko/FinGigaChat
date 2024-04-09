from aiogram.filters.callback_data import CallbackData

from constants.products import state_support as callback_prefixes


class GetStateSupportPDF(CallbackData, prefix=callback_prefixes.GET_STATE_SUPPORT_PDF):
    """Отправка пдф файлов по господдержке"""
    pass
