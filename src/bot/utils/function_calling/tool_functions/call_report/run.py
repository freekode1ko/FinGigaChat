import sqlalchemy as sa
from fuzzywuzzy import process
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from db import models
from db.database import async_session
from utils.function_calling.tool_functions.preparing_meeting.config import MESSAGE_RUN_CALL_REPORTS, DEBUG_GRAPH
from utils.function_calling.tool_functions.utils import send_status_message_for_agent


@tool
async def get_call_reports_by_name(name: str, config: RunnableConfig) -> str:
    """Возвращает текст с историей взаимодействия пользователя с данным клиентом.

    Args:
        name (str): название клиента в именительном падеже
    return:
        (str): суммаризованный текст предыдущих взаимодействий с пользователем.
    """
    if DEBUG_GRAPH:
        print(f'Вызвана функция get_call_reports_by_name с параметром {name}')

    await send_status_message_for_agent(config, MESSAGE_RUN_CALL_REPORTS)

    message = config['configurable']['message']
    user_id = message.from_user.id

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
        return '\n'.join(call_reports)
