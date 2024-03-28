from typing import Any

from configs import config


class ResearchFormatter:

    @classmethod
    def format(cls, research_row: dict[str, Any]) -> str:
        """
        Формирует сообщение на основе данных, хранящихся в базе, по собранному отчету

        :param research_row: dict[header, text, publication_date]
        return: Текст сообщения
        """
        # Список сообщений (длина списка > 1, если текст сообщения слишком длинный)
        formatted_text = (
            f'<b>{research_row["header"].capitalize()}:</b>\n\n'
            f'{research_row["text"]}\n'
            f'<i>Дата публикации: {research_row["publication_date"].strftime(config.BASE_DATE_FORMAT)}</i>'
        )

        return formatted_text
