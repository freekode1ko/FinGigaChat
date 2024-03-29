"""update_parser_source

Revision ID: 4effee5d98ff
Revises: 0c80ddce4b81
Create Date: 2024-03-29 16:15:44.154154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from db.models import ParserSource, SourceGroup


# revision identifiers, used by Alembic.
revision: str = '4effee5d98ff'
down_revision: Union[str, None] = '2e8cea167b16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade_update_row_in_parser_source(session: sa.orm.Session) -> None:
    stmt = (
        sa.update(ParserSource).
        where(ParserSource.source == 'https://tradingeconomics.com/commodities').
        values(name='Tradingeconomics Commodities', response_format=None)
    )
    session.execute(stmt)


def downgrade_update_row_in_parser_source(session: sa.orm.Session) -> None:
    stmt = (
        sa.update(ParserSource).
        where(ParserSource.source == 'https://tradingeconomics.com/commodities').
        values(name='Алюминий', response_format='Алюминий')
    )
    session.execute(stmt)


def upgrade_insert_row_in_parser_source(session: sa.orm.Session) -> None:
    stmt = sa.insert(ParserSource).values(
        name='LNG Japan/Korea',
        alt_names=[],
        source='https://www.investing.com/commodities/lng-japan-korea-marker-platts-futures',
        source_group_id=sa.select(SourceGroup.id).where(SourceGroup.name_latin == 'metals')
    )
    session.execute(stmt)


def downgrade_insert_row_in_parser_source(session: sa.orm.Session) -> None:
    stmt = sa.delete(ParserSource).where(
        source='https://www.investing.com/commodities/lng-japan-korea-marker-platts-futures'
    )
    session.execute(stmt)


def upgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    upgrade_update_row_in_parser_source(session)
    upgrade_insert_row_in_parser_source(session)
    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)
    downgrade_update_row_in_parser_source(session)
    downgrade_insert_row_in_parser_source(session)
    session.commit()
