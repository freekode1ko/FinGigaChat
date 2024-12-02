from pydantic import Field, computed_field

from api.v1.common_schemas import BaseReadModel, BaseWriteModel


class ProductDocumentRead(BaseReadModel):
    """Схема для вывода документа на чтение"""

    id: int
    file_path: str = Field(..., exclude=True)
    name: str
    description: str | None = None

    @computed_field
    def url(self) -> str:
        return f'/{self.file_path.lstrip("/code/").lstrip("/")}'


class ShortProductRead(BaseReadModel):
    """Схема для вывода продукта на чтение в упрощенном формате"""

    id: int
    name: str
    description: str | None = None
    display_order: int
    parent_id: int | None = None
    name_latin: str | None = None


class ProductRead(ShortProductRead):
    """
    Схема для вывода продукта на чтение. Включает все поля упрощенной схемы,
    а также списки документов и дочерних продуктов.
    """

    documents: list[ProductDocumentRead] = []
    children: list['ProductRead'] = []


ProductRead.model_rebuild()


class ProductUpdate(BaseWriteModel):
    """Схема для частичного обновления продукта"""

    name: str | None = None
    description: str | None = None
    display_order: int | None = None
    name_latin: str | None = None
    parent_id: int | None = None


class ProductCreate(BaseWriteModel):
    """Схема для создания нового продукта"""

    name: str
    description: str | None = None
    display_order: int
    name_latin: str | None = None
    parent_id: int
