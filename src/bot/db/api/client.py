from typing import Optional, Any

import sqlalchemy as sa
from sqlalchemy import text

from db import database, models
from db.api.subject_interface import SubjectInterface


def get_client_navi_link_by_name(client_name: str) -> Optional[str]:
    with database.engine.connect() as conn:
        query = text('SELECT navi_link FROM client WHERE LOWER(name)=:client_name LIMIT 1')
        navi_link = conn.execute(query.bindparams(client_name=client_name.lower())).scalar_one_or_none()

    return navi_link


async def get_research_type_id_by_name(client_name: str) -> Optional[dict[str, Any]]:
    async with database.async_session() as session:
        stmt = sa.select(models.ResearchType.id).where(
            models.ResearchType.name == client_name
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


client_db = SubjectInterface(models.Client, models.ClientAlternative, models.Client.client_alternative, models.RelationClientArticle.article)
