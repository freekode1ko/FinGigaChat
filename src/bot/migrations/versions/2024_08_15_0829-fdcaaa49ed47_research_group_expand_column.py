"""research_group_expand_column

Revision ID: fdcaaa49ed47
Revises: 46e15b229b90
Create Date: 2024-08-15 08:29:32.817378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdcaaa49ed47'
down_revision: Union[str, None] = '46e15b229b90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('research_group', sa.Column('display_order', sa.Integer(), nullable=True, server_default=sa.text('0'),
                                              comment='Порядок отображения групп'))
    op.add_column('research_group', sa.Column('expand', sa.Boolean(), server_default=sa.text('false'),
                                              comment='Флаг, указывающий, что вместо отображения группы, надо отобразить ее разделы'))


def downgrade() -> None:
    op.drop_column('research_group', 'display_order')
    op.drop_column('research_group', 'expand')
