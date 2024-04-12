from sqlalchemy import text, select

from db.database import engine
from db.models import Whitelist


def update_user_email(user_id: int, user_email: str):
    """Обновление почты существующего пользователя"""
    query = text('UPDATE whitelist SET user_email=:user_email WHERE user_id=:user_id')
    with engine.connect() as conn:
        conn.execute(query.bindparams(user_email=user_email.lower(), user_id=user_id))
        conn.commit()


def is_new_user_email(user_email: str) -> bool:
    """Проверка на наличие почты в таблице (занята кем-то или нет)"""
    query = text('SELECT user_email FROM whitelist WHERE LOWER(user_email)=:user_email')
    with engine.connect() as conn:
        return not conn.execute(query.bindparams(user_email=user_email.lower())).scalar()


def is_user_email_exist(user_id: int) -> bool:
    """Проверка наличия почты у пользователя"""
    query = select(Whitelist.user_email).where(Whitelist.user_id==user_id)
    with engine.connect() as conn:
        return conn.execute(query).scalar()
