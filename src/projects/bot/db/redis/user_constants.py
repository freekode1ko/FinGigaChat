"""Обработка времени последнего сообщения и фоновой задачи в Redis."""
from db.redis.client import redis_client

ACTIVITY_NAME = 'activity_'
FON_TASK_NAME = 'fon_task_'


async def get_user_constant(constant_name: str, user_id: int) -> str | None:
    """
    Получение пользовательской константы по ее имени.

    :param constant_name:   Имя константы в редис.
    :param user_id:         ID пользователя.
    :return:                Значение пользовательской константы.
    """
    name = constant_name + str(user_id)
    date = await redis_client.get(name)
    return date if date else None


async def update_user_constant(constant_name: str, user_id: int, value: str) -> None:
    """
    Обновление пользовательской константы по ее имени.

    :param constant_name:   Имя константы в редис.
    :param user_id:         ID пользователя.
    :param value:           Новое значение пользовательской константы.
    """
    name = constant_name + str(user_id)
    await redis_client.set(name, value)


async def del_user_constant(constant_name: str, user_id: int) -> None:
    """
    Удаление пользовательской константы по ее имени.

    :param constant_name:   Имя константы в редис.
    :param user_id:         ID пользователя.
    """
    name = constant_name + str(user_id)
    await redis_client.delete(name)
