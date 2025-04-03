"""Описание pydantic моделей для взаимодействия с сервисом мониторинга."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, NaiveDatetime

from configs.config import MOSCOW_TZ


class ParserBase(BaseModel):
    """Базовая модель парсера."""

    model_config = ConfigDict(from_attributes=True)

    name: str | int = Field(description='Имя парсера или его id')
    description: Optional[str] = Field(default=None, description='Описание парсера')
    is_critical: bool = Field(default=False, description='Флаг, что данные с парсера критично важны для системы источника')
    period_cron: str = Field(description='Выражение crona')
    alert_timedelta: Optional[int] = Field(default=None, description='Дельта, после которой отправляется уведомление, секунды')


class ParserCreate(ParserBase):
    """Модель для создания парсера."""


class ParserUpdate(ParserBase):
    """Модель для обновления парсера."""

    name: Optional[str | int] = None
    description: Optional[str] = None
    source_system_name: Optional[str] = None
    is_critical: Optional[bool] = None
    period_cron: Optional[str] = None
    alert_timedelta: Optional[int] = None
    last_update_datetime: Optional[NaiveDatetime] = Field(
        examples=[datetime.now(tz=MOSCOW_TZ).replace(tzinfo=None),],
        default=None,
        description='Дата и время последнего обновления'
    )


class ParserUpdateLastUpdateTime(BaseModel):
    """Модель для обновления даты последнего парсинга парсера."""

    name: str | int
    last_update_datetime: NaiveDatetime = Field(examples=[datetime.now(tz=MOSCOW_TZ).replace(tzinfo=None)])
