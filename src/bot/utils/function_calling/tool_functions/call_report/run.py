from humanfriendly.terminal import message
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from db.database import async_session
from db import models

import sqlalchemy as sa

from utils.function_calling.tool_functions.utils import parse_runnable_config
from fuzzywuzzy import process


@tool
async def get_call_reports_by_name(name: str, runnable_config: RunnableConfig):
    """Возвращает текст с историей взаимодействия пользователя с данным клиентом.

    Args:
        name (str): название клиента в именительном падеже
    return:
        (str): суммаризованный текст предыдущих взаимодействий с пользователем.
    """
    runnable_config = parse_runnable_config(runnable_config)
    user_id = runnable_config.message.from_user.id

    async with async_session() as session:
        # Список клиентов
        clients = await session.execute(
            sa.select(models.CallReports.client)
            .filter(models.CallReports.user_id == user_id)
            .distinct()
        )

        matches = process.extractBests(name, [_[0] for _ in clients.fetchall()], score_cutoff=95)
        if matches:
            best_match_client_name = matches[0][0]
        else:
            return 'По такому клиенту кол репортов нет'

        reports = await session.execute(
            sa.select(models.CallReports.description)
            .filter(
                models.CallReports.user_id == user_id,
                models.CallReports.client == best_match_client_name,
            )
            .order_by(models.CallReports.report_date)
            .limit(5)
        )
        call_reports: list[str] = reports.scalars().all()
        return call_reports


