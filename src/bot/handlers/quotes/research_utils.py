"""Методы для получения отчетов CIB Research"""

import re
from datetime import datetime
from typing import Any, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from constants.quotes.const import RESEARCH_REPORTS
from db.api.research import research_db
from log.bot_logger import logger


MONTH_NAMES_DICT = {
    1: 'янв', 2: 'фев', 3: 'мар', 4: 'апр', 5: 'мая', 6: 'июн',
    7: 'июл', 8: 'авг', 9: 'сен', 10: 'окт', 11: 'нояб', 12: 'дек'
}


def get_part_from_start_to_end(content, start, end=None) -> str:
    """
    Вернуть текст от start выражения до end выражения.

    :param content:   Текст.
    :param start:     Начальное выражение.
    :param end:       Конечно выражение.
    :return:          Получившийся текст.
    """
    pattern = rf'{start}(.*?)$' if end is None else rf'{start}(.*?)(?=\s*{end})'
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        return match.group(0)
    er_msg = f'Текст не подходит под паттерн {pattern}: {content}'
    logger.error(er_msg)
    raise ValueError(er_msg)


def get_until_upper_case(content: str) -> str:
    """Оставляем абзацы до строчки с UpperCase."""
    new_text_rows = []
    for row in content.split('\n\n'):
        if row.isupper():
            break
        new_text_rows.append(row)
    return '\n\n'.join(new_text_rows)


def format_date_to_cib_format(date_obj: datetime) -> str:
    """Форматирование даты в формат CIB Research."""
    formatted_date = f"{date_obj.day} {MONTH_NAMES_DICT[date_obj.month]}., '{str(date_obj.year)[2:]}"
    return formatted_date


async def get_reports_for_quotes(
        session: AsyncSession,
        report_key: str,
        format_func: Optional[Callable] = None
) -> list[list[str]]:
    """
    Получение отчетов по CIB Research.

    :param session:     Асинхронная сессия с бд.
    :param report_key:  Ключ, по которому нужно достать данные с параметрами запроса в бд.
    :param format_func: Ссылка на функцию форматирования.
    :return:            Список из списков атрибутов отчетов.
    """
    reports = []
    reports_data: list[dict[str, Any]] = RESEARCH_REPORTS[report_key]
    for data in reports_data:
        reports_ = await research_db.get_report_by_parameters(session, data)
        for r in reports_:
            reports.append(
                [
                    r.header,
                    format_func(r.text, **data.get('format_args', {})) if data.get('format') else r.text,
                    format_date_to_cib_format(r.publication_date)
                ]
            )
    return reports
