"""Обработка исторического запроса и истории диалога между пользователем и ботом в Redis."""

import json

from constants.constants import COUNT_OF_USEFUL_LAST_MSGS, KEEP_DIALOG_TIME
from db.redis.client import redis_client

HISTORY_QUERY_KEY = 'history_query_{chat_id}'


async def get_history_query(chat_id: int) -> str:
    """
    Получение исторически перефразированного запроса пользователя.

    :param chat_id: Telegram chat_id с пользователем.
    :return:        Исторически перефразированный запрос пользователя.
    """
    return await redis_client.get(HISTORY_QUERY_KEY.format(chat_id=chat_id)) or ''


async def update_history_query(chat_id: int, history_query: str) -> None:
    """
    Обновление исторически перефразированного запроса пользователя.

    :param chat_id:         Telegram chat_id с пользователем.
    :param history_query:   Исторически перефразированный запрос пользователя.
    """
    key = HISTORY_QUERY_KEY.format(chat_id=chat_id)
    await redis_client.setex(name=key, value=history_query, time=KEEP_DIALOG_TIME)


async def get_dialog(chat_id: int) -> list[dict[str, str]]:
    """
    Получение истории диалога между пользователем и ИИ.

    :param chat_id:         Telegram chat_id с пользователем.
    :return:                История диалога.
    """
    dialog = await redis_client.hget(str(chat_id), key='dialog')
    return json.loads(dialog) if dialog else []


async def update_dialog(chat_id: int, msgs: dict[str, str], need_replace: bool = False) -> None:
    """
    Обновление истории диалога.

    :param chat_id:        Telegram chat_id с пользователем.
    :param msgs:           Диалог из двух сообщений: пользователь и ИИ.
    :param need_replace:   Необходимость замены последних сообщений новыми.
    """
    dialog = await get_dialog(chat_id)
    if dialog:
        if need_replace:
            dialog.pop()
        dialog = dialog[-COUNT_OF_USEFUL_LAST_MSGS:]

    dialog.append(msgs)
    dialog_serialized = json.dumps(dialog)
    await redis_client.hset(str(chat_id), key='dialog', value=dialog_serialized)
    await redis_client.expire(name=str(chat_id), time=KEEP_DIALOG_TIME)


async def del_dialog_and_history_query(chat_id: int) -> None:
    """
    Очистка исторического запроса пользователя и истории диалога между пользователем и ИИ.

    :param chat_id:      Telegram chat_id с пользователем.
    """
    await redis_client.delete(str(chat_id))
    await redis_client.delete(HISTORY_QUERY_KEY.format(chat_id=chat_id))


async def get_last_user_msg(chat_id: int) -> str:
    """
    Получение последнего пользовательского запроса.

    :param chat_id:     Telegram chat_id c пользователем.
    :return:            Последний пользовательский запрос.
    """
    if dialog := await get_dialog(chat_id):
        return dialog[-1]['user']
    return ''
