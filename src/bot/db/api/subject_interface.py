from typing import Any

import pandas as pd
from sqlalchemy import select, func

from db import database


class SubjectInterface:

    def __init__(self, table, table_alternative, relation) -> None:
        self.table = table
        self.table_alternative = table_alternative
        self.relation = relation
        self.columns = [i.name for i in self.table.__table__.columns]
        self.fields = [getattr(self.table, c) for c in self.columns]

    async def get_all(self) -> pd.DataFrame:
        async with database.async_session() as session:
            stmt = select(
                *self.fields
            )
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=self.columns)

    async def get_by_industry_id(self, industry_id: int) -> pd.DataFrame:
        async with database.async_session() as session:
            stmt = select(
                *self.fields
            ).where(self.table.industry_id == industry_id)
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=self.columns)

    async def get_other_names(self) -> pd.DataFrame:
        async with database.async_session() as session:
            stmt = select(
                self.table.id,
                self.table.name,
                func.unnest(func.string_to_array(self.table_alternative.other_names, ';')).label('other_name'),
            ).outerjoin(self.relation)
            result = await session.execute(stmt)
            data = result.fetchall()
            return pd.DataFrame(data, columns=['id', 'name', 'other_name'])

    async def get(self, _id: int) -> dict[str, Any]:
        async with database.async_session() as session:
            stmt = select(self.table).where(self.table.id == _id)
            result = await session.execute(stmt)
            data = result.scalar()
            return {c: getattr(data, c) for c in self.columns}
