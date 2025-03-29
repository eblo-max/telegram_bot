from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Базовый класс для всех репозиториев."""

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Получить сущность по ID."""
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Сохранить сущность."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удалить сущность."""
        pass
