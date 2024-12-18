from typing import Any, Generic, TypeVar, Type, Sequence

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


T = TypeVar('T', bound=DeclarativeBase)


class GenericRepository(Generic[T]):
    """Базовый класс репозитория"""

    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Инициализация репозитория с сессией и моделью SQLAlchemy.

        :param session: Асинхронная сессия
        :param model: Модель
        """
        self._session = session
        self._model = model

    @property
    def _primary_key(self):
        """Первичный ключ модели"""
        return sa.inspect(self._model).primary_key[0]

    async def create(self, instance: T) -> None:
        """
        Добавляет запись в текущую сессию.

        :param instance: Экземпляр модели SQLAlchemy
        """
        self._session.add(instance)
        await self._session.commit()

    async def get_by_pk(self, pk: Any) -> T | None:
        """
        Возвращает запись по первичному ключу.

        :param pk: Значение первичного ключа искомого экземпляра
        :return: Экземпляр модели SQLAlchemy, если существует, иначе None
        """
        result = await self._session.execute(
            sa.select(self._model).where(self._primary_key == pk)
        )
        return result.scalars().first()

    async def get_list(self) -> Sequence[T]:
        """
        Возвращает список всех записей.

        :return: Список экземпляров модели SQLAlchamy
        """
        result = await self._session.execute(sa.select(self._model))
        return result.scalars().all()

    async def update(self, instance: T) -> None:
        """
        Добавляет обновленный экземпляр модели в сессию.

        :param instance: Экземпляр модели SQLAlchemy
        :return: Обновленный экземпляр модели
        """
        self._session.add(instance)
        await self._session.commit()

    async def delete(self, instance: T) -> None:
        """
        Удаляет запись из БД.

        :param instance: Экземпляр модели SQLAlchemy
        """
        await self._session.delete(instance)
        await self._session.commit()
