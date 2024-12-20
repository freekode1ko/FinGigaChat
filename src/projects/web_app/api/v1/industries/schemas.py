from pydantic import Field, computed_field

from api.v1.common_schemas import BaseReadModel, BaseWriteModel
from utils.utils import transform_path_to_link

class IndustryDocumentRead(BaseReadModel):
    """Схема для вывода документа отрасли на чтение"""

    id: int
    file_name: str = Field(..., alias="name")
    file_path: str = Field(..., exclude=True)

    @computed_field
    def url(self) -> str | None:
        return transform_path_to_link(self.file_path)


class IndustryRead(BaseReadModel):
    """Схема для вывода отрасли на чтение"""

    id: int
    name: str
    display_order: int
    documents: list[IndustryDocumentRead] = Field(default_factory=list)


class IndustryUpdate(BaseWriteModel):
    """Схема для частичного обновления отрасли"""

    name: str | None = None
    display_order: int | None = None


class IndustryCreate(BaseWriteModel):
    """Схема для создания новой отрасли"""

    name: str
    display_order: int
