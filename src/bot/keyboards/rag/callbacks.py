from aiogram.filters.callback_data import CallbackData


class RegenerateResponse(CallbackData, prefix='regenerate'):
    """Перегенерировать ответ от ИИ."""

    rephrase_query: bool  # использовать для генерации ответа перефразированный вопрос
    initially_query: bool  # использовать для генерации ответа изначальный вопрос пользователя
