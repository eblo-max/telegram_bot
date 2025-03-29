from typing import List, Optional, Dict
from uuid import UUID
import logging

from dark_archive.domain.interfaces.achievement_service import IAchievementService
from dark_archive.domain.interfaces.achievement_repository import IAchievementRepository
from dark_archive.domain.entities.achievement import Achievement
from dark_archive.domain.entities.player_achievement import PlayerAchievement

logger = logging.getLogger(__name__)


class AchievementService(IAchievementService):
    """Реализация сервиса достижений."""

    def __init__(self, repository: IAchievementRepository):
        self._repository = repository

    def check_achievements(self, player_id: UUID) -> List[Achievement]:
        """Проверяет и возвращает новые достижения игрока."""
        new_achievements = []
        all_achievements = self._repository.get_all()
        player_achievements = self._repository.get_player_achievements(player_id)
        player_achievement_ids = {a.id for a in player_achievements}

        for achievement in all_achievements:
            if achievement.id not in player_achievement_ids:
                progress = self._repository.get_player_achievement_progress(
                    player_id, achievement.id
                )
                if progress >= 1.0:
                    self._repository.save_player_achievement(player_id, achievement.id)
                    new_achievements.append(achievement)

        return new_achievements

    def get_player_achievements(self, player_id: UUID) -> List[Achievement]:
        """Получает список достижений игрока."""
        return self._repository.get_player_achievements(player_id)

    def get_achievement_by_id(self, achievement_id: UUID) -> Optional[Achievement]:
        """Получает достижение по ID."""
        return self._repository.get_by_id(achievement_id)

    def get_all_achievements(self) -> List[Achievement]:
        """Получает список всех доступных достижений."""
        return self._repository.get_all()

    def award_achievement(self, player_id: UUID, achievement_id: UUID) -> bool:
        """Награждает игрока достижением."""
        achievement = self._repository.get_by_id(achievement_id)
        if not achievement:
            return False

        player_achievements = self._repository.get_player_achievements(player_id)
        if achievement in player_achievements:
            return False

        self._repository.save_player_achievement(player_id, achievement_id)
        return True

    def get_achievement_progress(self, player_id: UUID, achievement_id: UUID) -> float:
        """Получает прогресс достижения для игрока (0.0 - 1.0)."""
        return self._repository.get_player_achievement_progress(
            player_id, achievement_id
        )

    def update_achievement_progress(
        self, player_id: UUID, achievement_id: UUID, progress: float
    ) -> None:
        """Обновляет прогресс достижения для игрока."""
        self._repository.update_player_achievement_progress(
            player_id, achievement_id, progress
        )

    def _check_criteria(self, criteria: Dict, context: Dict) -> float:
        """Check achievement criteria and return progress (0.0 - 1.0)."""
        try:
            criterion_type = criteria.get("type")
            if not criterion_type:
                return 0.0

            if criterion_type == "count":
                return self._check_count_criterion(criteria, context)
            elif criterion_type == "value":
                return self._check_value_criterion(criteria, context)
            elif criterion_type == "collection":
                return self._check_collection_criterion(criteria, context)
            else:
                logger.warning(f"Unknown criterion type: {criterion_type}")
                return 0.0
        except Exception as e:
            logger.error(f"Failed to check criteria: {e}")
            return 0.0

    def _check_count_criterion(self, criteria: Dict, context: Dict) -> float:
        """Check count-based criterion (e.g., solve X cases)."""
        try:
            target = criteria.get("target", 0)
            if target <= 0:
                return 0.0

            current = context.get(criteria.get("field", ""), 0)
            return min(1.0, current / target)
        except Exception as e:
            logger.error(f"Failed to check count criterion: {e}")
            return 0.0

    def _check_value_criterion(self, criteria: Dict, context: Dict) -> float:
        """Check value-based criterion (e.g., reach X points)."""
        try:
            target = criteria.get("target", 0)
            if target <= 0:
                return 0.0

            current = context.get(criteria.get("field", ""), 0)
            return min(1.0, current / target)
        except Exception as e:
            logger.error(f"Failed to check value criterion: {e}")
            return 0.0

    def _check_collection_criterion(self, criteria: Dict, context: Dict) -> float:
        """Check collection-based criterion (e.g., collect all items of type X)."""
        try:
            required = set(criteria.get("required", []))
            if not required:
                return 0.0

            collected = set(context.get(criteria.get("field", ""), []))
            return len(required.intersection(collected)) / len(required)
        except Exception as e:
            logger.error(f"Failed to check collection criterion: {e}")
            return 0.0
