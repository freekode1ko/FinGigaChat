from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
import traceback
import sqlalchemy as sa

from db import models
from fuzzywuzzy import process

from db.database import async_session
from utils.function_calling.tool_functions.preparing_meeting.config import MESSAGE_RUN_CIB_REPORTS, DEBUG_GRAPH
from utils.function_calling.tool_functions.utils import send_status_message_for_agent


@tool
async def get_analytical_reports_by_name(name: str, config: RunnableConfig) -> str:
    """Возвращает текст с аналитическими отчетами по компании по заданному названию компании.

    Args:
        name (str): только название компании в именительном падеже.
    return:
        (str): Текст с отчетами по компании.
    """
    # фин показатели
    # последний отчет
    if DEBUG_GRAPH:
        print(f'Вызвана функция get_research_reports_by_name с параметром: {name}')
    try:
        await send_status_message_for_agent(config, MESSAGE_RUN_CIB_REPORTS)

        async with async_session() as session:
            clients = await session.execute(
                sa.select(models.ResearchType.name, models.ResearchType.id)
            )
            clients = clients.fetchall()
            matches = process.extractBests(name, [_[0] for _ in clients], score_cutoff=95)
            if matches:
                best_match_client_name = matches[0][0]
                research_type_id = next(filter(lambda x: x[0] == best_match_client_name, clients))[1]
            else:
                return 'По такому клиенту нет отчетов CIB'
            reports = await session.execute(
                sa.select(models.Research.text)
                .join(models.ResearchResearchType)
                .filter(
                    models.ResearchResearchType.research_type_id == research_type_id,
                )
                .order_by(models.Research.publication_date.desc())
                .limit(1)
            )
    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return reports.scalars().all()
