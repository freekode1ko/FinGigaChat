import datetime as dt
from typing import Any

from sqlalchemy import select, insert, CursorResult

from db.models import UserMeeting, Whitelist
from db.database import engine
from config import REMEMBER_TIME


def data_as_dict(data: CursorResult) -> list[dict[str, Any]]:
    """Преобразование результата запроса в список из словарей, где ключи - имена полей"""
    return [data_part._asdict() for data_part in data]


def get_user_email(user_id: int | str) -> str:
    """
    Получение почты пользователя по его id.

    :param user_id: id пользователя
    :return: почта пользователя
    """
    if isinstance(user_id, str):
        user_id = int(user_id)

    with engine.connect() as conn:
        query = select(Whitelist.user_email).where(Whitelist.user_id==user_id)
        email = conn.execute(query)
        return email.scalar()


def add_meeting(data: dict[str, Any]) -> None:
    """
    Добавление новой встречи пользователя в бд.

    :param data: данные о встрече
    """
    user_timezone = data['timezone']

    query = insert(UserMeeting).values(
        user_id=int(data['user_id']),
        theme=data['theme'],
        description=data['description'],
        date_start=data['date_start'],
        date_end=data['date_end'],
        timezone=user_timezone
    )
    with engine.connect() as conn:
        conn.execute(query)
        conn.commit()


def get_user_meetings(user_id: int | str) -> list[dict[str, Any]]:
    """
    Получение всех предстоящих и идущих встреч пользователя.

    :param user_id: id пользователя
    :return: Список из словарей с информацией о встречах
    """
    if isinstance(user_id, str):
        user_id = int(user_id)

    dt_utc_now = dt.datetime.now(dt.timezone.utc)
    dt_utc_now = dt.datetime(dt_utc_now.year, dt_utc_now.month, dt_utc_now.day, dt_utc_now.hour, dt_utc_now.minute)

    query = (select(UserMeeting.theme, UserMeeting.date_start, UserMeeting.timezone).
             where(UserMeeting.user_id == user_id).
             where(UserMeeting.date_end > dt_utc_now)
             )
    with engine.connect() as conn:
        meetings = conn.execute(query)
        return data_as_dict(meetings)


def get_user_meetings_for_notification() -> list[dict[str, Any]]:
    """Получение всех предстоящих встреч для реализации напоминаний"""
    minutes = REMEMBER_TIME['last']['minutes']
    dt_utc_now = dt.datetime.now(dt.timezone.utc)
    min_start_time = dt.datetime(dt_utc_now.year, dt_utc_now.month,
                                 dt_utc_now.day, dt_utc_now.hour, dt_utc_now.minute + minutes)
    query = (select(UserMeeting.user_id, UserMeeting.theme, UserMeeting.date_start, UserMeeting.timezone).
             # where(UserMeeting.is_notify_first == False or
             #       UserMeeting.is_notify_second == False or  #TODO: refactor
             #       UserMeeting.is_notify_last == False).
             where(UserMeeting.date_start > min_start_time))
    with engine.connect() as conn:
        meetings = conn.execute(query)
        return data_as_dict(meetings)
