import json
import logging
from typing import Any, Optional
from redis import Redis
from dark_archive.application.interfaces.cache_service import CacheService

logger = logging.getLogger(__name__)


class RedisCacheService(CacheService):
    """Сервис кэширования в Redis"""

    def __init__(self, redis_client: Redis, prefix: str = "cache"):
        self.redis = redis_client
        self.prefix = prefix

    def _get_key(self, key: str) -> str:
        """Форматирует ключ с префиксом"""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша"""
        try:
            value = await self.redis.get(self._get_key(key))
            if value is None:
                return None
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при десериализации значения из кэша: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении значения из кэша: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохраняет значение в кэш"""
        try:
            serialized_value = json.dumps(value)
            result = await self.redis.set(
                self._get_key(key), serialized_value, ex=ttl if ttl else None
            )
            return bool(result)
        except (TypeError, json.JSONEncodeError) as e:
            logger.error(f"Ошибка при сериализации значения для кэша: {e}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при сохранении значения в кэш: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Удаляет значение из кэша"""
        try:
            result = await self.redis.delete(self._get_key(key))
            return bool(result)
        except Exception as e:
            logger.error(f"Ошибка при удалении значения из кэша: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Проверяет существование ключа в кэше"""
        try:
            return bool(await self.redis.exists(self._get_key(key)))
        except Exception as e:
            logger.error(f"Ошибка при проверке существования ключа в кэше: {e}")
            return False
