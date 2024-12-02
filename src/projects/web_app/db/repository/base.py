from typing import Any, Generic, TypeVar, Type

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
        Добавляет экземпляр модели в текущую сессию.

        :param instance: Экземпляр модели
        """
        self._session.add(instance)
        await self._session.commit()

    async def get_by_pk(self, pk: Any) -> T | None:
        """
        Возвращает экземпляр модели по первичному ключу.

        :param pk: Значение первичного ключа искомого экземпляра
        :return: Экземпляр модели, если существует, иначе None
        """
        result = await self._session.execute(
            sa.select(self._model).where(self._primary_key == pk)
        )
        return result.scalars().first()

    async def get_list(self) -> list[T]:
        """
        Возвращает список всех экземпляров модели. Не поддерживает
        фильтры или пагинацию.

        :return: Список экземпляров модели
        """
        result = await self._session.execute(sa.select(self._model))
        return list(result.scalars().all())

    async def update(self, instance: T) -> None:
        """
        Добавляет обновленный экземпляр модели в сессию.

        :param instance: Экземпляр модели
        :return: Обновленный экземпляр модели
        """
        self._session.add(instance)
        await self._session.commit()

    async def delete(self, pk: Any) -> bool:
        """
        Удаляет экземпляр модели из БД по первичному ключу.

        :param pk: Значение первичного ключа удаляемого экземпляра
        :return: True, если экземпляр был найден и удален, иначе False
        """
        stmt = (
            sa.delete(self._model)
            .where(self._primary_key == pk)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0
