"""Работа с историей диалога между пользователем и ИИ."""
import re

from configs.prompts import NEW_QUERY_BY_DIALOG_PROMPT
from db.api.user_dialog_history import user_dialog_history_db
from log.bot_logger import logger
import module.gigachat as gig


chat = gig.GigaChat(logger)
COUNT_OF_USEFUL_LAST_MSGS = 6


def _make_rephrase_query_by_history(query: str, dialog: list[dict[str, str]]) -> str:
    """
    Создание нового запроса на основе пользовательского с помощью истории диалога.

    :param query:   Запрос пользователя.
    :param dialog:  Исторические сообщения из бд.
    :return:        Переписанный (если нужно) на основе диалога запрос пользователя.
    """
    if not dialog:
        return query

    history = '\n'.join([
        f'Пользователь: {mini_dialog["user"]}\n ИИ: {mini_dialog["ai"]}\n'
        for mini_dialog in dialog[:-COUNT_OF_USEFUL_LAST_MSGS:-1]
    ])

    text = NEW_QUERY_BY_DIALOG_PROMPT.format(query=query, history=history)
    giga_answer = chat.get_giga_answer(text=text)
    return giga_answer


async def get_rephrase_query(user_id: int, full_name: str, query: str) -> str:
    """
    Получение нового запроса на основе пользовательского с помощью истории диалога.

    :param user_id:     Telegram id пользователя.
    :param full_name:   Полное имя пользователя.
    :param query:       Запрос пользователя.
    :return:            Переписанный (если нужно) на основе диалога запрос пользователя.
    """
    user_dialog_history = await user_dialog_history_db.get_user_dialog(user_id)
    rephrase_query = _make_rephrase_query_by_history(query, user_dialog_history['dialog'])

    if matches := re.findall(r'Пользователь:(.*?)(?:\n|$)', rephrase_query):
        rephrase_query = matches[-1]
    rephrase_query = rephrase_query.strip()

    logger.info(f'*{user_id}* {full_name} - "{query}" : По истории диалога сформирован запрос: "{rephrase_query}"')
    return rephrase_query
