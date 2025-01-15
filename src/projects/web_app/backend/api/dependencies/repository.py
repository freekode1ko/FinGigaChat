from typing import Callable, Type

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_async_session
from db.repository.base import GenericRepository


def get_repository(
    repository_type: Type[GenericRepository],
) -> Callable[[AsyncSession], GenericRepository]:
    """
    Создает и возвращает экземпляр репозитория для какой-то модели.

    :param repository_type: Конкретная реализация репозитория, наследующаяся от GenericRepository
    :return: Экземпляр данного репозитория
    """
    def _get_repo(
        async_session: AsyncSession = Depends(get_async_session),
    ) -> GenericRepository:
        return repository_type(session=async_session)
    return _get_repo
