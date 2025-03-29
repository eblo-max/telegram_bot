from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from uuid import UUID

from dark_archive.domain.interfaces.lifecycle_manager import ILifecycleManager

T = TypeVar("T")


class Repository(ILifecycleManager, Generic[T], ABC):
    """Базовый интерфейс репозитория."""

    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        """Получает сущность по идентификатору."""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Получает все сущности."""
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Сохраняет сущность."""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Обновляет сущность."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Удаляет сущность."""
        pass
