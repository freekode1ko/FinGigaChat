"""add new feature_type

Revision ID: 553511343eb7
Revises: b26eb4f29660
Create Date: 2024-10-17 09:34:25.237936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from db.models import Feature
from migrations.data.add_new_feature_type.data import BOT_FEATURES_DATA

# revision identifiers, used by Alembic.
revision: str = '553511343eb7'
down_revision: Union[str, None] = 'b26eb4f29660'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def add_features(
        session: sa.orm.Session,
        data: dict[str, str],
):
    """
    Создание, сохранение объектов.

    :param session: Сессия бд.
    :param data:    Данные для создания экземпляров модели.
    """
    objs = [Feature(name=name, description=desc) for name, desc in data.items()]
    session.add_all(objs)
    session.commit()


def delete_features(
        session: sa.orm.Session,
        data: dict[str, str],
):
    """
    Удаление объектов.

    :param session: Сессия бд.
    :param data:    Данные для удаления экземпляров модели.
    """
    session.execute(sa.delete(Feature).where(Feature.name.in_(data.keys())))
    session.commit()


def upgrade() -> None:
    conn = op.get_bind()
    session = sa.orm.Session(bind=conn)
    add_features(session, BOT_FEATURES_DATA)


def downgrade() -> None:
    conn = op.get_bind()
    session = sa.orm.Session(bind=conn)
    delete_features(session, BOT_FEATURES_DATA)
