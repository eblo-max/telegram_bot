from typing import List, Optional
from uuid import UUID
import json
import logging

from redis import Redis

from dark_archive.domain.interfaces.achievement_repository import IAchievementRepository
from dark_archive.domain.entities.achievement import Achievement
from dark_archive.domain.entities.player_achievement import PlayerAchievement
from dark_archive.infrastructure.serialization.json_serializer import JsonSerializer
from dark_archive.application.interfaces.repository import Repository

logger = logging.getLogger(__name__)


class RedisAchievementRepository(Repository):
    """Redis реализация репозитория достижений."""

    def __init__(self, redis_client: Redis, prefix: str = "achievement"):
        self._redis = redis_client
        self._prefix = prefix
        self._serializer = JsonSerializer()
        self._achievement_prefix = "achievement:"
        self._player_achievement_prefix = "player:achievement:"
        self._player_progress_prefix = "player:progress:"

    def _achievement_key(self, achievement_id: UUID) -> str:
        """Get Redis key for achievement."""
        return f"{self._prefix}:achievement:{str(achievement_id)}"

    def _player_achievement_key(self, player_id: UUID, achievement_id: UUID) -> str:
        """Get Redis key for player achievement."""
        return (
            f"{self._prefix}:player:{str(player_id)}:achievement:{str(achievement_id)}"
        )

    def _player_achievements_key(self, player_id: UUID) -> str:
        """Get Redis key for player achievements set."""
        return f"{self._prefix}:player:{str(player_id)}:achievements"

    def create_achievement(self, achievement: Achievement) -> None:
        try:
            key = self._achievement_key(achievement.id)
            data = self._serializer.serialize(achievement)
            self._redis.set(key, json.dumps(data))
            logger.info(f"Created achievement {achievement.id}")
        except Exception as e:
            logger.error(f"Failed to create achievement: {e}")
            raise

    def get_achievement_by_id(self, achievement_id: UUID) -> Optional[Achievement]:
        try:
            key = self._achievement_key(achievement_id)
            data = self._redis.get(key)
            if not data:
                return None
            achievement_data = json.loads(data)
            return self._serializer.deserialize(achievement_data, Achievement)
        except Exception as e:
            logger.error(f"Failed to get achievement {achievement_id}: {e}")
            return None

    def get_all_achievements(self) -> List[Achievement]:
        try:
            pattern = f"{self._prefix}:achievement:*"
            keys = self._redis.keys(pattern)
            achievements = []
            for key in keys:
                data = self._redis.get(key)
                if data:
                    achievement_data = json.loads(data)
                    achievement = self._serializer.deserialize(
                        achievement_data, Achievement
                    )
                    achievements.append(achievement)
            return achievements
        except Exception as e:
            logger.error(f"Failed to get all achievements: {e}")
            return []

    def update_achievement(self, achievement: Achievement) -> None:
        try:
            key = self._achievement_key(achievement.id)
            if not self._redis.exists(key):
                raise ValueError(f"Achievement {achievement.id} does not exist")
            achievement.update()
            data = self._serializer.serialize(achievement)
            self._redis.set(key, json.dumps(data))
            logger.info(f"Updated achievement {achievement.id}")
        except Exception as e:
            logger.error(f"Failed to update achievement: {e}")
            raise

    def delete_achievement(self, achievement_id: UUID) -> None:
        try:
            key = self._achievement_key(achievement_id)
            if self._redis.delete(key):
                logger.info(f"Deleted achievement {achievement_id}")
            else:
                logger.warning(f"Achievement {achievement_id} not found for deletion")
        except Exception as e:
            logger.error(f"Failed to delete achievement: {e}")
            raise

    def get_player_achievements(self, player_id: UUID) -> List[PlayerAchievement]:
        try:
            pattern = f"{self._prefix}:player:{str(player_id)}:achievement:*"
            keys = self._redis.keys(pattern)
            achievements = []
            for key in keys:
                data = self._redis.get(key)
                if data:
                    achievement_data = json.loads(data)
                    achievement = self._serializer.deserialize(
                        achievement_data, PlayerAchievement
                    )
                    achievements.append(achievement)
            return achievements
        except Exception as e:
            logger.error(f"Failed to get player achievements: {e}")
            return []

    def get_player_achievement(
        self, player_id: UUID, achievement_id: UUID
    ) -> Optional[PlayerAchievement]:
        try:
            key = self._player_achievement_key(player_id, achievement_id)
            data = self._redis.get(key)
            if not data:
                return None
            achievement_data = json.loads(data)
            return self._serializer.deserialize(achievement_data, PlayerAchievement)
        except Exception as e:
            logger.error(f"Failed to get player achievement: {e}")
            return None

    def save_player_achievement(self, player_achievement: PlayerAchievement) -> None:
        try:
            key = self._player_achievement_key(
                player_achievement.player_id, player_achievement.achievement_id
            )
            data = self._serializer.serialize(player_achievement)
            self._redis.set(key, json.dumps(data))

            # Add to player's achievement set if completed
            if player_achievement.completed:
                set_key = self._player_achievements_key(player_achievement.player_id)
                self._redis.sadd(set_key, str(player_achievement.achievement_id))

            logger.info(
                f"Saved player achievement for player {player_achievement.player_id}"
            )
        except Exception as e:
            logger.error(f"Failed to save player achievement: {e}")
            raise

    def get_achievement_count(self, player_id: UUID) -> int:
        try:
            set_key = self._player_achievements_key(player_id)
            return self._redis.scard(set_key)
        except Exception as e:
            logger.error(f"Failed to get achievement count: {e}")
            return 0

    def get_total_points(self, player_id: UUID) -> int:
        try:
            set_key = self._player_achievements_key(player_id)
            achievement_ids = self._redis.smembers(set_key)
            total_points = 0

            for achievement_id in achievement_ids:
                achievement = self.get_achievement_by_id(UUID(achievement_id))
                if achievement:
                    total_points += achievement.points

            return total_points
        except Exception as e:
            logger.error(f"Failed to get total points: {e}")
            return 0

    def save(self, achievement: Achievement) -> None:
        """Сохраняет достижение."""
        key = f"{self._achievement_prefix}{achievement.id}"
        data = self._serializer.serialize(achievement)
        self._redis.set(key, data)

    def get_by_category(self, category: str) -> List[Achievement]:
        """Получает достижения по категории."""
        achievements = self.get_all_achievements()
        return [a for a in achievements if a.category == category]

    def get_player_achievement_progress(
        self, player_id: UUID, achievement_id: UUID
    ) -> float:
        """Получает прогресс достижения для игрока."""
        key = f"{self._player_progress_prefix}{player_id}:{achievement_id}"
        progress = self._redis.get(key)
        return float(progress) if progress else 0.0

    def update_player_achievement_progress(
        self, player_id: UUID, achievement_id: UUID, progress: float
    ) -> None:
        """Обновляет прогресс достижения для игрока."""
        key = f"{self._player_progress_prefix}{player_id}:{achievement_id}"
        self._redis.set(key, str(progress))
