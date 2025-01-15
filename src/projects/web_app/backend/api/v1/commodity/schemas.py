from pydantic import Field, computed_field

from api.v1.common_schemas import BaseReadModel
from utils.utils import transform_path_to_link


class CommodityResearchRead(BaseReadModel):
    """Схема для вывода исследований по commodities на чтение"""
    id: int
    title: str | None
    text: str
    file_name: str | None

    @computed_field
    def url(self) -> str | None:
        return transform_path_to_link(f'/sources/commodity_reports/{self.file_name}') if self.file_name else None


class CommodityRead(BaseReadModel):
    """Схема для вывода commodity на чтение"""
    id: int
    name: str
    industry_id: int | None
    commodity_research : list[CommodityResearchRead] = Field(default_factory=list)
