from pydantic_settings import BaseSettings

from constants.constants import END_BUTTON_TXT


class RAGTexts(BaseSettings):

    RAG_CLEAR_HISTORY: str = 'История диалога очищена!'

    RAG_FINISH_STATE: str = f'Напишите «{END_BUTTON_TXT}» для завершения общения с Базой Знаний'
    RAG_START_STATE: str = 'Начато общение с Базой Знаний\n\n' + RAG_FINISH_STATE
    RAG_FIRST_USER_QUERY: str = 'Подождите...\nФормирую ответ на запрос: "{query}"\n' + RAG_FINISH_STATE

    RAG_TRY_AGAIN: str = 'Напишите, пожалуйста, свой запрос еще раз'
    RAG_ERROR_ANSWER: str = 'Извините, я пока не могу ответить на ваш запрос.'

    RAG_LIKE_FEEDBACK: str = 'Я рад, что вам понравилось!'
    RAG_DISLIKE_FEEDBACK: str = 'Я буду стараться лучше...'

    RAG_GIGA_RAG_FOOTER: str = (
        'Ответ сгенерирован Gigachat с помощью Базы Знаний. '
        'Информация требует дополнительной верификации.'
    )

    RAG_FORMAT_ANSWER: str = '{answer}\n\n' + RAG_GIGA_RAG_FOOTER
