"""Обработка исторического запроса и истории диалога между пользователем и ботом в Redis."""

import json

from constants.constants import COUNT_OF_USEFUL_LAST_MSGS, KEEP_DIALOG_TIME
from db.redis.client import redis_client

HISTORY_QUERY_KEY = 'history_query_{user_id}'


async def get_history_query(user_id: int) -> str:
    """
    Получение исторически перефразированного запроса пользователя.

    :param user_id: Telegram id пользователя.
    :return:        Исторически перефразированный запрос пользователя.
    """
    history_query = await redis_client.get(HISTORY_QUERY_KEY.format(user_id=user_id))
    return history_query if history_query else ''


async def update_history_query(user_id: int, history_query: str) -> None:
    """
    Обновление исторически перефразированного запроса пользователя.

    :param user_id:         Telegram id пользователя.
    :param history_query:   Исторически перефразированный запрос пользователя.
    """
    key = HISTORY_QUERY_KEY.format(user_id=user_id)
    await redis_client.setex(name=key, value=history_query, time=KEEP_DIALOG_TIME)


async def get_dialog(user_id: int) -> list[dict[str, str]]:
    """
    Получение истории диалога между пользователем и ИИ.

    :param user_id:         Telegram id пользователя.
    :return:                История диалога.
    """
    dialog = await redis_client.hget(str(user_id), key='dialog')
    return json.loads(dialog) if dialog else []


async def update_dialog(user_id: int, msgs: dict[str, str], need_replace: bool = False) -> None:
    """
    Обновление истории диалога.

    :param user_id:        Telegram id пользователя.
    :param msgs:           Диалог из двух сообщений: пользователь и ИИ.
    :param need_replace:   Необходимость замены последних сообщений новыми.
    """
    dialog = await get_dialog(user_id)
    if dialog:
        if need_replace:
            dialog.pop()
        dialog = dialog[-COUNT_OF_USEFUL_LAST_MSGS:]

    dialog.append(msgs)
    dialog_serialized = json.dumps(dialog)
    await redis_client.hset(str(user_id), key='dialog', value=dialog_serialized)
    await redis_client.expire(name=str(user_id), time=KEEP_DIALOG_TIME)


async def del_dialog_and_history_query(user_id: int) -> None:
    """
    Очистка исторического запроса пользователя и истории диалога между пользователем и ИИ.

    :param user_id:      Telegram id пользователя.
    """
    await redis_client.delete(str(user_id))
    await redis_client.delete(HISTORY_QUERY_KEY.format(user_id=user_id))


async def get_last_user_msg(user_id: int) -> str:
    """
    Получение последнего пользовательского запроса.

    :param user_id:     Telegram id пользователя.
    :return:            Последний пользовательский запрос.
    """
    if dialog := await get_dialog(user_id):
        return dialog[-1]['user']
    return ''
