"""Обработка истории диалога между пользователем и ботом в Redis."""

import json

from constants.constants import COUNT_OF_USEFUL_LAST_MSGS, KEEP_DIALOG_TIME
from db.redis.client import redis_client


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


async def del_dialog(user_id: int) -> None:
    """
    Очистка истории диалога между пользователем и ИИ.

    :param user_id:      Telegram id пользователя.
    """
    await redis_client.delete(str(user_id))


async def get_last_user_msg(user_id: int) -> str:
    """
    Получение последнего пользовательского запроса.

    :param user_id:     Telegram id пользователя.
    :return:            Последний пользовательский запрос.
    """
    dialog = await get_dialog(user_id)
    if dialog:
        return dialog[-1]['user']
    return ''
