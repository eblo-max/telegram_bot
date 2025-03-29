from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from dark_archive.domain.models.case import Case, CaseStatus


class ICaseRepository(ABC):
    """Интерфейс репозитория для работы с делами"""

    @abstractmethod
    async def create(self, case: Case) -> None:
        """Создает новое дело"""
        pass

    @abstractmethod
    async def get(self, case_id: UUID) -> Optional[Case]:
        """Получает дело по id"""
        pass

    @abstractmethod
    async def get_by_status(self, status: CaseStatus) -> List[Case]:
        """Получает список дел по статусу"""
        pass

    @abstractmethod
    async def update(self, case: Case) -> None:
        """Обновляет дело"""
        pass

    @abstractmethod
    async def delete(self, case_id: UUID) -> None:
        """Удаляет дело"""
        pass
