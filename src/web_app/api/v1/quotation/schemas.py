from typing import Optional

from pydantic import BaseModel


class Param(BaseModel):
    """Параметры, которые могут быть у элементов"""
    
    name: str
    value: Optional[float]


class DataItem(BaseModel):
    """"Элементы для дашбордов"""

    name: str
    value: Optional[float]
    params: list[Param]


class SectionData(BaseModel):
    """"Секции для дашбордов"""

    section_name: str
    data: list[DataItem]


class ExchangeSectionData(BaseModel):
    """"Список секций для дашбордов"""

    sections: list[SectionData]
