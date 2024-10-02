import datetime
from enum import Enum, IntEnum
from typing import Optional

from pydantic import BaseModel

# from constants.constants import ids_to_type
from db.models import SizeEnum


class Param(BaseModel):
    """Параметры, которые могут быть у элементов"""

    name: str
    value: Optional[float]

class DataItem(BaseModel):
    """"Элементы для дашбордов"""
    quote_id: int
    name: str
    ticker: str | None = None
    params: Optional[list[Param]]

    value: Optional[float] = 0
    view_type: SizeEnum = SizeEnum.TEXT

    research_item_id: Optional[int] = None
    tv_type: Optional[str] = None
    image_path: Optional[str] = None


class BaseSection(BaseModel):
    """"Секции котировок"""
    section_name: str


class SectionData(BaseSection):
    """"Секции для дашбордов"""

    section_params: Optional[list[str]]
    data: list[DataItem]


class ExchangeSectionData(BaseModel):
    """"Список секций для дашбордов"""

    sections: list[SectionData]


class SubscriptionItem(BaseModel):
    """Элемент подписки"""

    id: int
    name: str
    ticker: str | None = None
    active: bool
    type: SizeEnum = SizeEnum.TEXT


class SubscriptionSection(BaseSection):
    """Секция подписок"""

    subscription_items: list[SubscriptionItem]


class DashboardSubscriptions(BaseModel):
    """Секции подписок"""

    subscription_sections: list[SubscriptionSection]


class GraphData(BaseModel):
    """Данные для графиков за день"""

    date: datetime.date
    value: float | None = None
    open: float | None = None
    close: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None


class DashboardGraphData(BaseModel):
    """Данные для графика"""

    id: int
    data: list[GraphData]
