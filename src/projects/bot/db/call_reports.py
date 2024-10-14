"""Функции в БД для рабы с call report'ами"""
from sqlalchemy import func, select

from db.database import async_session
from db.models import CallReports, RegisteredUser


async def get_all_sorted_clients_for_user(user_id: int) -> list[str]:
    """
    Функция для получения всех клиентов у пользователя

    :param user_id: айди пользователя
    """
    async with async_session() as session:
        clients = await session.execute(
            select(CallReports.client)
            .filter(CallReports.user_id == user_id)
            .distinct()
        )
        return sorted([_[0] for _ in clients.fetchall()])


async def get_all_dates_for_client_report(user_id: int, client_name: str) -> list[tuple[int, str]]:
    """
    Функция для получения всех дат по клиенту у пользователя

    :param user_id: айди пользователя
    :param client_name: имя клиента
    """
    async with async_session() as session:
        client_call_reports_dates = await session.execute(
            select(CallReports.id, CallReports.report_date).filter(
                CallReports.user_id == user_id,
                func.lower(CallReports.client) == client_name.lower(),
            )
            .distinct()
        )
        return sorted(client_call_reports_dates.fetchall(), key=lambda _: _[1])


async def get_user_email_async(user_id: int | str) -> str:
    """
    Асинхронное получение почты пользователя по его id

    :param user_id: id пользователя
    :return: почта пользователя
    """
    user_id = int(user_id)

    async with async_session() as session:
        email = await session.execute(select(RegisteredUser.user_email).where(RegisteredUser.user_id == user_id))
        return email.scalar()
