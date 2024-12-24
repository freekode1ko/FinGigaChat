import math
from typing import TypeVar, Generic

from fastapi import Query
from pydantic import BaseModel, ConfigDict

from db.pagination import Pagination


T = TypeVar('T')


class BaseReadModel(BaseModel):
    """Базовая схема модели на чтение"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BaseWriteModel(BaseModel):
    """Базовая схема модели на запись (создание / обновление)"""
    model_config = ConfigDict(str_strip_whitespace=True, extra='ignore', allow_inf_nan=False)


class Error(BaseModel):
    """Модель ошибки."""
    detail: str


class PaginationParams(BaseModel):
    """
    Параметры пагинации.

    Метод parse_params() выполняет преобразование параметров и возвращает
    экземпляр класса Pagination, который содержит атрибуты limit и offset.
    """
    page: int = Query(1, ge=1, description="Номер страницы")
    size: int = Query(10, ge=1, le=100, description="Размер страницы")

    def to_db(self) -> Pagination:
        return Pagination(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )


class PaginatedResponse(BaseReadModel, Generic[T]):
    items: list[T]
    total_items: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total_items: int,
        page_size: int,
    ) -> 'PaginatedResponse[T]':
        total_pages = math.ceil(total_items / page_size) if page_size > 0 else 1
        return cls(
            items=items,
            total_items=total_items,
            total_pages=total_pages,
        )
