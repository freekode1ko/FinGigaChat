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

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.research_item_id, self.tv_type, self.image_path = self.get_other_info()
    #
    # def get_other_info(self) -> tuple[Optional[int], Optional[str], Optional[str]]:
    #     """Получить айди для запросов к CIB, тип для графиков trading view и картинку"""
    #     for i in ids_to_type:
    #         if self.name in i.names:
    #             return i.research_type_id, i.tv_type, i.image_path  # FXIME
    #     return (None,) * 3


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
    """"""

    id: int
    name: str
    ticker: str | None = None
    active: bool
    type: SizeEnum = SizeEnum.TEXT


class SubscriptionSection(BaseSection):
    subscription_items: list[SubscriptionItem]


class DashboardSubscriptions(BaseModel):
    subscription_sections: list[SubscriptionSection]


class GraphData(BaseModel):
    """"""

    date: datetime.date
    value: float | None = None
    open: float | None = None
    close: float | None = None
    high: float | None = None
    low: float | None = None
    volume: float | None = None


class DashboardGraphData(BaseModel):
    """"""

    id: int
    data: list[GraphData]
