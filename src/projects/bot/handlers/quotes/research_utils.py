"""Методы для получения отчетов CIB Research"""

import re
from datetime import datetime
from typing import Any, Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from constants.enums import QuotesType
from constants.quotes.const import ReportParameter, RESEARCH_REPORTS_PARAMETERS
from db.api.research import research_db
from log.bot_logger import logger


MONTH_NAMES = (None, 'янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'нояб', 'дек')


def get_part_from_start_to_end(content: str, start: str, end: Optional[str] = None) -> str:
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
    return f"{date_obj.day} {MONTH_NAMES[date_obj.month]}., '{str(date_obj.year)[2:]}"


async def get_reports_for_quotes(
        session: AsyncSession,
        report_key: QuotesType,
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
    reports_data: list[ReportParameter[str, Any]] = RESEARCH_REPORTS_PARAMETERS[report_key]
    for data in reports_data:
        data = data.dict()
        reports_db = await research_db.get_report_by_parameters(session, data)
        for r in reports_db:
            reports.append(
                [
                    r.header,
                    format_func(r.text, **data['format_args']) if data['format'] else r.text,
                    format_date_to_cib_format(r.publication_date)
                ]
            )
    return reports
