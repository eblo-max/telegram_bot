import json
from typing import Dict, List, Optional
from uuid import UUID
import logging
from redis import Redis

from dark_archive.domain.models.case import Case, CaseStatus
from dark_archive.domain.interfaces.case_repository import ICaseRepository
from dark_archive.infrastructure.serialization.json_serializer import JsonSerializer
from dark_archive.application.interfaces.repository import Repository
from dark_archive.domain.entities.case import Case
from dark_archive.domain.repositories.case_repository import CaseRepository

logger = logging.getLogger(__name__)


class RedisCaseRepository(CaseRepository):
    """Redis репозиторий для работы с делами."""

    def __init__(self, redis_client: Redis, prefix: str = "case"):
        self._redis = redis_client
        self._prefix = prefix
        self._serializer = JsonSerializer()
        self._cases: dict[UUID, Case] = {}

    def _get_key(self, case_id: UUID) -> str:
        """Формирует ключ для Redis"""
        return f"{self._prefix}:{str(case_id)}"

    def _get_status_key(self, status: CaseStatus) -> str:
        """Формирует ключ для множества дел с определенным статусом"""
        return f"{self._prefix}:status:{status}"

    async def create(self, case: Case) -> None:
        """Создает новое дело"""
        try:
            key = self._get_key(case.id)
            status_key = self._get_status_key(case.status)

            # Сериализуем дело
            case_data = self._serializer.serialize(case)

            # Сохраняем дело
            await self._redis.set(key, json.dumps(case_data))

            # Добавляем ID дела в множество по статусу
            await self._redis.sadd(status_key, str(case.id))

            logger.debug(f"Created case {case.id} in Redis")
        except Exception as e:
            logger.error(f"Failed to create case in Redis: {str(e)}")
            raise

    async def get_by_id(self, case_id: UUID) -> Optional[Case]:
        """Получает дело по ID"""
        try:
            key = self._get_key(case_id)
            data = await self._redis.get(key)

            if not data:
                return None

            case_data = json.loads(data)
            return self._serializer.deserialize(case_data, Case)
        except Exception as e:
            logger.error(f"Failed to get case {case_id} from Redis: {str(e)}")
            return None

    async def get_by_status(self, status: CaseStatus) -> List[Case]:
        """Получает список дел по статусу"""
        try:
            status_key = self._get_status_key(status)
            case_ids = await self._redis.smembers(status_key)

            cases = []
            for case_id in case_ids:
                case = await self.get_by_id(UUID(case_id))
                if case:
                    cases.append(case)

            return cases
        except Exception as e:
            logger.error(f"Failed to get cases by status from Redis: {str(e)}")
            return []

    async def update(self, case: Case) -> None:
        """Обновляет существующее дело"""
        try:
            key = self._get_key(case.id)
            old_case = await self.get_by_id(case.id)

            if not old_case:
                raise ValueError(f"Case {case.id} not found")

            # Если статус изменился, обновляем множества
            if old_case.status != case.status:
                old_status_key = self._get_status_key(old_case.status)
                new_status_key = self._get_status_key(case.status)

                await self._redis.srem(old_status_key, str(case.id))
                await self._redis.sadd(new_status_key, str(case.id))

            # Сохраняем обновленное дело
            case_data = self._serializer.serialize(case)
            await self._redis.set(key, json.dumps(case_data))

            logger.debug(f"Updated case {case.id} in Redis")
        except Exception as e:
            logger.error(f"Failed to update case in Redis: {str(e)}")
            raise

    async def delete(self, case_id: UUID) -> None:
        """Удаляет дело"""
        try:
            key = self._get_key(case_id)
            old_case = await self.get_by_id(case_id)

            if old_case:
                # Удаляем из множества по статусу
                status_key = self._get_status_key(old_case.status)
                await self._redis.srem(status_key, str(case_id))

                # Удаляем само дело
                await self._redis.delete(key)

                logger.debug(f"Deleted case {case_id} from Redis")
        except Exception as e:
            logger.error(f"Failed to delete case from Redis: {str(e)}")
            raise

    def save(self, case: Case) -> Case:
        """Сохранение дела."""
        self._cases[case.id] = case
        return case

    def get(self, case_id: UUID) -> Optional[Case]:
        """Получение дела по ID."""
        return self._cases.get(case_id)

    def get_all(self) -> List[Case]:
        """Получение всех дел."""
        return list(self._cases.values())

    def delete(self, case_id: UUID) -> None:
        """Удаление дела."""
        if case_id in self._cases:
            del self._cases[case_id]
