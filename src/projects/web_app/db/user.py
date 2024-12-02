from sqlalchemy import (
    select,
    func,
)
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import RegisteredUser


async def is_new_user_email(session: AsyncSession, email: str) -> bool:
    """Проверка на наличие почты в таблице (занята кем-то или нет)

    :param AsyncSession session: Сессия SQLAlchemy
    :param str email: Почта пользователя
    :return: True, если пользователя с такой почтой нет в БД, иначе False
    """
    query = select(RegisteredUser.user_email).where(func.lower(RegisteredUser.user_email) == email.lower())
    result = await session.execute(query)
    return not result.scalar()


async def get_user_id_by_email(session: AsyncSession, email: str) -> int:
    """Получение идентификатора пользователя по его email.

    :param AsyncSession session: Сессия SQLAlchemy
    :param str email: Почта пользователя
    :return: Идентификатор пользователя
    """
    query = select(RegisteredUser.user_id).where(RegisteredUser.user_email == email)
    id_ = await session.execute(query)
    return int(id_.scalar())


async def get_user_by_id(session: AsyncSession, user_id: int) -> RegisteredUser:
    """Получение модели пользователя по его идентификатору.

    :param AsyncSession session: Сессия SQLAlchemy
    :param int user_id: Идентификатор пользователя
    :return: SQLAlchemy объект пользователя
    """
    query = select(RegisteredUser).where(RegisteredUser.user_id == user_id)
    user = await session.execute(query)
    return user.scalars().first()
