"""Модель статуса парсера"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, NaiveDatetime


class Statuses(str, Enum):
    """Виды статусов парсеров"""

    ok = 'В порядке'
    error = 'Не отвечает'
    unspecified = 'Информация отсутствует'


class ParserStatusSend(BaseModel):
    """Модель статуса парсера при его отправке в сервис мониторинга"""

    param_value: str = Field(description='Наимпнование парсера (хост или иное)')
    status: Optional[Statuses] = Field(default=Statuses.unspecified, description='Статус парсера от команды GigaParser')
    parser_type: str = Field(description='Тип котировки')
    last_update_datetime: Optional[NaiveDatetime] = Field(default_factory=datetime.now,
                                                          description='Время последнего обновления (в UTC)')
    previous_update_datetime: Optional[NaiveDatetime] = Field(default=None,
                                                              description='Время предыдущего обновления (в UTC)')
