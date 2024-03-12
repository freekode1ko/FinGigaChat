from sqlalchemy import text

from db.database import engine


def update_user_email(user_id: int, user_email: str):
    """Обновление почты существующего пользователя"""
    query = text('UPDATE whitelist SET user_email=:user_email WHERE user_id=:user_id')
    with engine.connect() as conn:
        conn.execute(query.bindparams(user_email=user_email, user_id=user_id))
        conn.commit()