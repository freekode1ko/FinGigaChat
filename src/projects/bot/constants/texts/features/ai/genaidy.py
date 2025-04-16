"""Модуль с текстовками GenAiDy-сервиса."""
from pydantic_settings import BaseSettings

from constants.constants import END_BUTTON_TXT


class GenAiTexts(BaseSettings):
    """Класс для РАГ текстовок."""

    ASK_GEN_AI: str = 'Спросить у Геннадия'

    GEN_AI_FINISH_STATE: str = f'Напишите «{END_BUTTON_TXT}» для завершения общения'
    GEN_AI_START_STATE: str = (
        '👋 Привет! Меня зовут GenАIдий – цифровой сотрудник ДКК. Вот что я умею:\n'
        '📁 готовлю материалы для подготовки к встречам с клиентом\n'
        '📊 отвечаю на вопросы в свободной форме на основе новостей и материалов наших аналитиков\n\n'
        'Чем могу помочь сегодня? 😊'
    )
    GEN_AI_CAPTURE_MESSAGE: str = (
        '👋 Привет! Меня зовут GenАIдий – цифровой сотрудник ДКК. Сейчас я попробую помочь вам с вашим запросом 😊'
    )

    GEN_AI_WAITING_ANSWER: str = 'Подождите...\nФормирую ответ на запрос: "{query}"'

    GEN_AI_TRY_AGAIN: str = 'Напишите, пожалуйста, свой запрос еще раз'
    GEN_AI_ERROR_ANSWER: str = 'Извините, я пока не могу ответить на ваш запрос.'
