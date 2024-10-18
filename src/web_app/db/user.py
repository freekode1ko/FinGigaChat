from sqlalchemy import (
    select,
    func,
)

from db.models import RegisteredUser
from db.database import async_session


async def is_new_user_email(email: str) -> bool:
    """Проверка на наличие почты в таблице (занята кем-то или нет)

    :param str email: Почта пользователя
    :return: True, если пользователя с такой почтой нет в БД, иначе False
    """
    query = select(RegisteredUser.user_email).where(func.lower(RegisteredUser.user_email) == email.lower())
    async with async_session() as session:
        result = await session.execute(query)
        return not result.scalar()


async def get_user_id_by_email(email: str) -> int:
    """Получение идентификатора пользователя по его email.

    :param str email: Почта пользователя
    :return: Идентификатор пользователя
    """
    query = select(RegisteredUser.user_id).where(RegisteredUser.user_email == email)
    async with async_session() as session:
        id_ = await session.execute(query)
        return int(id_.scalar())


async def get_user_by_id(user_id: int) -> RegisteredUser:
    query = select(RegisteredUser).where(RegisteredUser.user_id == user_id)
    async with async_session() as session:
        user = await session.execute(query)
        return user.scalars().first()
