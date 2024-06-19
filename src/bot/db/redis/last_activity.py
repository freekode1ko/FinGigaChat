"""Обработка времени последнего сообщения от бота в Redis."""
from db.redis.client import redis_client

ACTIVITY_NAME = 'activity_{user_id}'


async def get_last_activity(user_id: int) -> str | None:
    """
    Получение времени последнего сообщения от бота.

    :param user_id: ID пользователя.
    :return:        Время последнего сообщения от бота.
    """
    name = ACTIVITY_NAME.format(user_id=user_id)
    date = await redis_client.get(name)
    return date if date else None


async def update_last_activity(user_id: int, activity_date: str) -> None:
    """
    Обновление времени последнего сообщения от бота.

    :param user_id:         ID пользователя.
    :param activity_date:   Новое время последнего сообщения от бота.
    """
    name = ACTIVITY_NAME.format(user_id=user_id)
    await redis_client.set(name, activity_date)
