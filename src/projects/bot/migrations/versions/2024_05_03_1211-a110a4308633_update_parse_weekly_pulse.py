"""update_parse_weekly_pulse

Revision ID: a110a4308633
Revises: f68463ef31e6
Create Date: 2024-05-03 12:11:36.023332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from db import models


# revision identifiers, used by Alembic.
revision: str = 'a110a4308633'
down_revision: Union[str, None] = 'f68463ef31e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    session.execute(
        sa.update(
            models.ParserSource
        ).where(models.ParserSource.name == 'Weekly Pulse').values(
            params={
                "p_p_id": "cibfxmmpublicationportlet_WAR_cibpublicationsportlet_INSTANCE_ezos",
                "p_p_lifecycle": "2",
                "p_p_state": "normal",
                "p_p_mode": "view",
                "p_p_resource_id": "getPublications",
                "p_p_cacheability": "cacheLevelPage",
            },
            alt_names=['^Research Weekly Pulse'],
        )
    )


def downgrade() -> None:
    pass
