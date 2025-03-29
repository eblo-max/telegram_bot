from typing import Dict, Optional, List
from uuid import UUID
from dataclasses import dataclass, field

from dark_archive.application.interfaces.repository import Repository
from dark_archive.domain.entities.achievement import Achievement


@dataclass
class MemoryAchievementRepository(Repository[Achievement]):
    """Репозиторий достижений в памяти для тестирования."""

    _achievements: Dict[UUID, Achievement] = field(default_factory=dict)
    _initialized: bool = False

    async def initialize(self) -> bool:
        """Инициализирует репозиторий."""
        self._initialized = True
        return True

    async def shutdown(self) -> bool:
        """Завершает работу репозитория."""
        self._initialized = False
        return True

    def is_healthy(self) -> bool:
        """Проверяет здоровье репозитория."""
        return self._initialized

    async def get(self, id: UUID) -> Optional[Achievement]:
        """Получает достижение по идентификатору."""
        return self._achievements.get(id)

    async def get_all(self) -> List[Achievement]:
        """Получает все достижения."""
        return list(self._achievements.values())

    async def save(self, achievement: Achievement) -> Achievement:
        """Сохраняет достижение."""
        self._achievements[achievement.id] = achievement
        return achievement

    async def update(self, achievement: Achievement) -> Achievement:
        """Обновляет достижение."""
        if achievement.id not in self._achievements:
            raise ValueError(f"Achievement with id {achievement.id} not found")
        self._achievements[achievement.id] = achievement
        return achievement

    async def delete(self, id: UUID) -> None:
        """Удаляет достижение."""
        if id in self._achievements:
            del self._achievements[id]
