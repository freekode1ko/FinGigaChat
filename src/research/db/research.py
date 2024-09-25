"""Методы по взаимодействию с таблицей research."""
import datetime as dt
from typing import Optional

import sqlalchemy as sa

from db.database import async_session
from db.models import Research


async def update_parent_report_ids(child_parent: dict[str, str]) -> None:
    """
    Обновление значений parent_report_id для вложенных в них отчетов.

    :param child_parent: {child_report_id: parent_report_id} - маленький отчет -> большой отчет (текста отчетов могут совпадать)
    """
    async with async_session() as conn:
        for child_id, parent_id in child_parent.items():
            await conn.execute(
                sa.update(Research)
                .where(Research.report_id == child_id)
                .values(parent_report_id=parent_id)
            )
        await conn.commit()


async def get_old_reports_for_period(
        min_date_of_report: dt.date,
        max_date_of_report: dt.date,
        new_reports_ids: Optional[list[str]] = None,
) -> list[Research]:
    """
    Получение старых отчетов за определенный период.

    :param min_date_of_report:  Минимальная дата для старых отчетов.
    :param max_date_of_report:  Максимальная дата для старых отчетов.
    :param new_reports_ids:     Список report_id новых отчетов.
    :return:                    Список с отчетами.
    """
    async with async_session() as conn:
        res = await conn.scalars(
            sa.select(Research)
            .where(Research.publication_date >= min_date_of_report)
            .where(Research.publication_date <= max_date_of_report)
            .where(Research.report_id.notin_(new_reports_ids))
        )
        return res.all()
