from aiogram.filters.callback_data import CallbackData


class RegenerateResponse(CallbackData, prefix='regenerate'):
    """Перегенерировать ответ от ИИ."""

    pass
