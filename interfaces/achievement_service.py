from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from dark_archive.domain.entities.achievement import Achievement


class IAchievementService(ABC):
    """Интерфейс сервиса достижений."""

    @abstractmethod
    async def check_achievements(self, player_id: UUID) -> List[Achievement]:
        """Проверяет и возвращает новые достижения игрока."""
        pass

    @abstractmethod
    async def get_player_achievements(self, player_id: UUID) -> List[Achievement]:
        """Получает список достижений игрока."""
        pass

    @abstractmethod
    async def get_achievement_by_id(
        self, achievement_id: UUID
    ) -> Optional[Achievement]:
        """Получает достижение по ID."""
        pass

    @abstractmethod
    async def get_all_achievements(self) -> List[Achievement]:
        """Получает список всех доступных достижений."""
        pass

    @abstractmethod
    async def award_achievement(self, player_id: UUID, achievement_id: UUID) -> bool:
        """Награждает игрока достижением."""
        pass

    @abstractmethod
    async def get_achievement_progress(
        self, player_id: UUID, achievement_id: UUID
    ) -> float:
        """Получает прогресс достижения для игрока (0.0 - 1.0)."""
        pass

    @abstractmethod
    async def update_achievement_progress(
        self, player_id: UUID, achievement_id: UUID, progress: float
    ) -> None:
        """Обновляет прогресс достижения для игрока."""
        pass
