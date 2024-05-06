"""new_message_type

Revision ID: 50aa3408b432
Revises: f68463ef31e6
Create Date: 2024-05-06 10:56:50.672410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from db import models

revision: str = '50aa3408b432'
down_revision: Union[str, None] = 'a110a4308633'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    session.execute(
        sa.insert(models.MessageType),
        [
            {
                'name': 'cib_research_newsletter',
                'is_default': False,
                'description': 'Рассылка отчетов с CIB Research',
            }
        ],
    )


def downgrade() -> None:
    pass
