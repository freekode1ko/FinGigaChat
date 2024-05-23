"""Работа с перефразированием запроса пользователя."""
import re

from configs.prompts import AUGMENT_SYSTEM_PROMPT, AUGMENT_MESSAGE_PROMPT, NEW_QUERY_BY_DIALOG_PROMPT
from db.api.user_dialog_history import user_dialog_history_db
from log.bot_logger import logger
import module.gigachat as gig


chat = gig.GigaChat(logger)
COUNT_OF_USEFUL_LAST_MSGS = 5


async def _make_rephrase_query_by_history(query: str, dialog: list[dict[str, str]]) -> str:
    """
    Создание нового запроса на основе пользовательского с помощью истории диалога.

    :param query:   Запрос пользователя.
    :param dialog:  Исторические сообщения из бд.
    :return:        Переписанный (если нужно) на основе диалога запрос пользователя.
    """
    if not dialog:
        return query
    history = '\n'.join([
        f'Пользователь: {mini_dialog["user"]}\nБот: {mini_dialog["ai"]}'
        for mini_dialog in dialog[-COUNT_OF_USEFUL_LAST_MSGS:]
    ])
    text = NEW_QUERY_BY_DIALOG_PROMPT.format(query=query, history=history)
    giga_answer = await chat.aget_giga_answer(text=text, prompt=AUGMENT_SYSTEM_PROMPT, temperature=0.01)
    return giga_answer


async def get_rephrase_query_by_history(user_id: int, full_name: str, query: str) -> str:
    """
    Получение нового запроса на основе пользовательского с помощью истории диалога.

    :param user_id:     Telegram id пользователя.
    :param full_name:   Полное имя пользователя.
    :param query:       Запрос пользователя.
    :return:            Переписанный (если нужно) на основе диалога запрос пользователя.
    """
    user_dialog_history = await user_dialog_history_db.get_user_dialog(user_id)
    rephrase_query = await _make_rephrase_query_by_history(query, user_dialog_history['dialog'])

    if matches := re.findall(r'Отдельный вопрос:(.*?)(?:\n|$)', rephrase_query):
        rephrase_query = matches[-1]
    rephrase_query = rephrase_query.strip()
    logger.info(f'*{user_id}* {full_name} - "{query}" : По истории диалога сформирован запрос: "{rephrase_query}"')
    return rephrase_query


async def _make_rephrase_query(query: str) -> str:
    """
    Создание нового запроса на основе пользовательского.

    :param query:   Запрос пользователя.
    :return:        Переписанный запрос пользователя.
    """
    text = AUGMENT_MESSAGE_PROMPT.format(query=query)
    giga_answer = await chat.aget_giga_answer(text=text, prompt=AUGMENT_SYSTEM_PROMPT)
    return giga_answer


async def get_rephrase_query(user_id: int, full_name: str, query: str) -> str:
    """
    Получение нового запроса на основе пользовательского.

    :param user_id:     Telegram id пользователя.
    :param full_name:   Полное имя пользователя.
    :param query:   Запрос пользователя.
    :return:        Переписанный запрос пользователя.
    """
    rephrase_query = await _make_rephrase_query(query)
    if matches := re.findall(r'Пользователь:(.*?)(?:\n|$)', rephrase_query):
        rephrase_query = matches[-1]
    rephrase_query = rephrase_query.strip()

    logger.info(f'*{user_id}* {full_name} - "{query}" : По истории диалога сформирован запрос: "{rephrase_query}"')
    return rephrase_query
