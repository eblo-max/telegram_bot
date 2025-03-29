# Created by setup script

from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheService(ABC):
    """Интерфейс сервиса кэширования"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохраняет значение в кэш"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Удаляет значение из кэша"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Проверяет существование ключа в кэше"""
        pass
