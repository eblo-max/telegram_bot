# Created by setup script

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from dark_archive.domain.entities.case import Case
from dark_archive.domain.enums import CaseStatus


class CaseRepository(ABC):
    """Интерфейс репозитория для работы с делами."""

    @abstractmethod
    async def create(self, case: Case) -> None:
        """Создает новое дело."""
        pass

    @abstractmethod
    async def get_by_id(self, case_id: str) -> Optional[Case]:
        """Получить дело по id."""
        pass

    @abstractmethod
    async def get_all_by_status(self, status: CaseStatus) -> List[Case]:
        """Получает все дела с указанным статусом."""
        pass

    @abstractmethod
    async def update(self, case: Case) -> None:
        """Обновляет дело."""
        pass

    @abstractmethod
    async def delete(self, case_id: UUID) -> None:
        """Удаляет дело."""
        pass

    @abstractmethod
    async def get_related_cases(self, case_id: UUID) -> List[Case]:
        """Получает связанные расследования."""
        pass

    @abstractmethod
    def save(self, case: Case) -> Case:
        """Сохранение дела."""
        pass

    @abstractmethod
    def get(self, case_id: UUID) -> Optional[Case]:
        """Получение дела по ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Case]:
        """Получение всех дел."""
        pass
