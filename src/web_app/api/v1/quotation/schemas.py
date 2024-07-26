from typing import Optional

from pydantic import BaseModel

from constants.constants import ids_to_type


class Param(BaseModel):
    """Параметры, которые могут быть у элементов"""

    name: str
    value: Optional[float]


class DataItem(BaseModel):
    """"Элементы для дашбордов"""

    name: str
    value: Optional[float]
    params: list[Param]
    research_item_id: Optional[int] = None
    tv_type: str = 'TVC:GOLD'  # FIXME
    image_path: Optional[str] = 'static/img/test_img.svg'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.research_item_id = self.get_id()

    def get_id(self) -> int | None:
        """Получить айди для запросов к CIB"""
        for i in ids_to_type:
            if self.name in i['name']:
                return i['research_type_id']
        return 19  # FIXME


class SectionData(BaseModel):
    """"Секции для дашбордов"""

    section_name: str
    section_params: Optional[list[str]]
    data: list[DataItem]


class ExchangeSectionData(BaseModel):
    """"Список секций для дашбордов"""

    sections: list[SectionData]
