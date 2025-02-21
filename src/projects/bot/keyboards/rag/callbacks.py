"""CallbackData для рага"""
from typing import Literal

from aiogram.filters.callback_data import CallbackData


class SetReaction(CallbackData, prefix='set_reaction'):
    """Поставить реакцию на ответ от Раг по вопросу пользователя."""

    user_msg_id: int
    reaction: Literal['like', 'dislike']


class RegenerateResponse(CallbackData, prefix='regenerate'):
    """Перегенерировать ответ от ИИ."""

    need_rephrase_query: bool  # нужно ли перефразировать вопрос для генерации ответа
    initially_query: bool  # использовать для генерации ответа изначальный вопрос пользователя


class GetReports(CallbackData, prefix='show_reports'):
    """Посмотреть отчеты, на основе которых генерировался ответ РАГа."""

    pass
