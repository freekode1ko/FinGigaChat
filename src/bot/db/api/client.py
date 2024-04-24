from typing import Optional

from sqlalchemy import text

from db import database
from db.api.subject_interface import SubjectInterface
from db.models import Client, ClientAlternative


def get_client_navi_link_by_name(client_name: str) -> Optional[str]:
    with database.engine.connect() as conn:
        query = text('SELECT navi_link FROM client WHERE LOWER(name)=:client_name LIMIT 1')
        industry_name = conn.execute(query.bindparams(client_name=client_name.lower())).scalar_one_or_none()

    return industry_name


client_db = SubjectInterface(Client, ClientAlternative, Client.client_alternative)
