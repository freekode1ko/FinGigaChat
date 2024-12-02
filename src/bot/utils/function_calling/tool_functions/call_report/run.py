import sqlalchemy as sa
from fuzzywuzzy import process
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from constants import constants
from db import models
from db.database import async_session
from main import bot
from utils.function_calling.tool_functions.utils import parse_runnable_config


@tool
async def get_call_reports_by_name(name: str, config: RunnableConfig) -> str:
    """Возвращает текст с историей взаимодействия пользователя с данным клиентом.

    Args:
        name (str): название клиента в именительном падеже
    return:
        (str): суммаризованный текст предыдущих взаимодействий с пользователем.
    """
    message = config['configurable']['message']
    buttons = config['configurable']['buttons']
    message_text = config['configurable']['message_text']
    final_message = config['configurable']['final_message']
    task_text = config['configurable']['task_text']

    message_text.append('-Обработка Call Report`ов\n')
    message_text.append(f'<blockquote expandable>{task_text}</blockquote>\n\n')

    await final_message.edit_text(''.join(message_text) + f'\n...', parse_mode='HTML')

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
