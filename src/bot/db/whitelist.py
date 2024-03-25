from sqlalchemy import text

from db.database import engine


def update_user_email(user_id: int, user_email: str):
    """Обновление почты существующего пользователя"""
    query = text('UPDATE whitelist SET user_email=:user_email WHERE user_id=:user_id')
    with engine.connect() as conn:
        conn.execute(query.bindparams(user_email=user_email, user_id=user_id))
        conn.commit()


def is_new_user_email(user_email: str) -> bool:
    """Проверка на наличие почты в таблице"""
    query = text('SELECT user_email FROM whitelist WHERE user_email=:user_email')
    with engine.connect() as conn:
        return not conn.execute(query.bindparams(user_email=user_email)).scalar()
