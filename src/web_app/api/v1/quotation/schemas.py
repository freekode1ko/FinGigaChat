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
    tv_type: Optional[str] = None
    image_path: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.research_item_id, self.tv_type, self.image_path = self.get_other_info()

    def get_other_info(self) -> tuple[Optional[int], Optional[str], Optional[str]]:
        """Получить айди для запросов к CIB, тип для графиков trading view и картинку"""
        for i in ids_to_type:
            if self.name in i.names:
                return i.research_type_id, i.tv_type, i.image_path
        return (None,) * 3


class SectionData(BaseModel):
    """"Секции для дашбордов"""

    section_name: str
    section_params: Optional[list[str]]
    data: list[DataItem]


class ExchangeSectionData(BaseModel):
    """"Список секций для дашбордов"""

    sections: list[SectionData]
