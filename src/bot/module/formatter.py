"""
Форматирует данные об отчете для выдачи пользователю.

Форматирование для выдачи полной версии отчета.
Форматирование для выдачи сокращенной версии отчета.
"""
from typing import Any

import pandas as pd

from configs import config
from constants.texts import texts_manager
from db import models


class ResearchFormatter:
    """Класс форматирования данных отчета для формирования сообщений"""

    @classmethod
    def format(cls, research: models.Research) -> str:
        """
        Сформировать сообщение на основе данных, хранящихся в базе, по собранному отчету

        :param research: Отчет CIB Research из БД
        :return:         Текст сообщения
        """
        formatted_text = (
            f'<b>{research.header}:</b>\n\n'
            f'{research.text}\n\n'
            # f'<i>Дата публикации: {research_row["publication_date"].strftime(config.BASE_DATE_FORMAT)}</i>\n'
            f'Источник: {texts_manager.REPOSRT_SOURCE}\n'
            # f'подробнее на <a href="{config.RESEARCH_SOURCE_URL}{research.report_id}" >портале</a>\n'
        )

        return formatted_text

    @classmethod
    def format_min(cls, research_row: dict[str, Any] | pd.Series) -> str:
        """
        Сформировать сообщение на основе данных, хранящихся в базе, по собранному отчету

        :param research_row: dict[header, text, publication_date, report_id]
        :return: Текст сообщения
        """
        formatted_text = (
            f'<b>{research_row["header"]}:</b>\n\n'
            f'<i>Дата публикации: {research_row["publication_date"].strftime(config.BASE_DATE_FORMAT)}</i>\n'
            f'Источник: {texts_manager.REPOSRT_SOURCE}\n'
            # f'подробнее на <a href="{config.RESEARCH_SOURCE_URL}{research_row["report_id"]}" >портале</a>\n'
        )

        return formatted_text
