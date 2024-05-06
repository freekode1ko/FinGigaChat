from typing import Any

import pandas as pd

from configs import config


class ResearchFormatter:

    @classmethod
    def format(cls, research_row: dict[str, Any] | pd.Series) -> str:
        """
        Формирует сообщение на основе данных, хранящихся в базе, по собранному отчету

        :param research_row: dict[header, text, publication_date, report_id]
        return: Текст сообщения
        """
        # Список сообщений (длина списка > 1, если текст сообщения слишком длинный)
        formatted_text = (
            f'<b>{research_row["header"]}:</b>\n\n'
            f'{research_row["text"]}\n\n'
            f'<i>Дата публикации: {research_row["publication_date"].strftime(config.BASE_DATE_FORMAT)}</i>\n'
            f'Источник: Sber CIB Research, подробнее на '
            f'<a href="{config.RESEARCH_SOURCE_URL}{research_row["report_id"]}" >портале</a>\n'
        )

        return formatted_text
