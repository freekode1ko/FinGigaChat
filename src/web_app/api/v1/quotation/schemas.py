from typing import List, Optional

from pydantic import BaseModel


class Param(BaseModel):
    name: str
    value: Optional[float]


class DataItem(BaseModel):
    name: str
    value: Optional[float]
    params: List[Param]


class SectionData(BaseModel):
    section_name: str
    data: List[DataItem]


class ExchangeSectionData(BaseModel):
    sections: List[SectionData]
