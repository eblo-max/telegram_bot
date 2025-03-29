from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from dark_archive.domain.entities.achievement import Achievement
from dark_archive.domain.entities.player_achievement import PlayerAchievement


class IAchievementRepository(ABC):
    """Interface for achievement repository operations."""

    @abstractmethod
    def create_achievement(self, achievement: Achievement) -> None:
        """Create a new achievement."""
        pass

    @abstractmethod
    def get_achievement_by_id(self, achievement_id: UUID) -> Optional[Achievement]:
        """Get achievement by ID."""
        pass

    @abstractmethod
    def get_all_achievements(self) -> List[Achievement]:
        """Get all available achievements."""
        pass

    @abstractmethod
    def update_achievement(self, achievement: Achievement) -> None:
        """Update an existing achievement."""
        pass

    @abstractmethod
    def delete_achievement(self, achievement_id: UUID) -> None:
        """Delete an achievement."""
        pass

    @abstractmethod
    def get_player_achievements(self, player_id: UUID) -> List[PlayerAchievement]:
        """Get all achievements for a player."""
        pass

    @abstractmethod
    def get_player_achievement(
        self, player_id: UUID, achievement_id: UUID
    ) -> Optional[PlayerAchievement]:
        """Get specific achievement for a player."""
        pass

    @abstractmethod
    def save_player_achievement(self, player_achievement: PlayerAchievement) -> None:
        """Save or update player achievement."""
        pass

    @abstractmethod
    def get_achievement_count(self, player_id: UUID) -> int:
        """Get total number of achievements earned by player."""
        pass

    @abstractmethod
    def get_total_points(self, player_id: UUID) -> int:
        """Get total achievement points earned by player."""
        pass
