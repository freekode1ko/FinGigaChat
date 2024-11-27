from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

import sqlalchemy as sa
from db import models
from fuzzywuzzy import process

from db.database import async_session


@tool
async def get_cib_reports_by_name(name: str, config: RunnableConfig) -> str:
    """Возвращает пользователю текст с отчетами из источника "CIB аналитика" по компании по заданному названию компании.

    Args:
        name (str): только название компании в именительном падеже.
    return:
        (str): Текст с отчетами по компании.
    """
    # фин показатели
    # последний отчет
    print(f'Вызвана функция get_cib_reports_by_name с параметром: {name}')
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
            .order_by(models.Research.publication_date)
            .limit(1)
        )

    return reports.scalars().all()