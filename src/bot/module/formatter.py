from typing import Any

from configs import config


class ResearchFormatter:

    @classmethod
    def format(cls, research_section_name: str, research_row: dict[str, Any]) -> str:
        """
        Формирует сообщение на основе данных, хранящихся в базе, по собранному отчету

        :param research_section_name: Название раздела отчета
        :param research_row: dict[header, text, publication_date, news_id]
        return: Текст сообщения
        """
        # Список сообщений (длина списка > 1, если текст сообщения слишком длинный)
        formatted_text = (
            f'{research_section_name}\n'
            f'{research_row["header"]}:\n\n'
            f'{research_row["text"]}\n\n'
            f'Дата публикации: {research_row["publication_date"].strftime(config.BASE_DATE_FORMAT)}\n'
            f'Источник: Sber CIB Research, подробнее на портале:'
            f'{config.RESEARCH_SOURCE_URL}{research_row["news_id"]}\n'
        )

        return formatted_text
