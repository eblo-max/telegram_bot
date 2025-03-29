from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from uuid import UUID

from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect


class ICaseRepository(ABC):
    """Интерфейс репозитория дел."""

    @abstractmethod
    async def get(self, case_id: UUID) -> Optional[Case]:
        """Получает дело по идентификатору."""
        pass

    @abstractmethod
    async def get_by_player_id(self, player_id: UUID) -> List[Case]:
        """Получает все дела игрока."""
        pass

    @abstractmethod
    async def get_active_case(self, player_id: UUID) -> Optional[Case]:
        """Получает активное дело игрока."""
        pass

    @abstractmethod
    async def save(self, case: Case) -> Case:
        """Сохраняет дело."""
        pass

    @abstractmethod
    async def update(self, case: Case) -> Case:
        """Обновляет дело."""
        pass

    @abstractmethod
    async def delete(self, case_id: UUID) -> None:
        """Удаляет дело."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Case]:
        """Получает все дела."""
        pass

    @abstractmethod
    async def create(self, case: Case) -> None:
        """Создает новое дело

        Args:
            case: Объект дела для создания
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[Case]:
        """Получает все дела пользователя

        Args:
            user_id: ID пользователя

        Returns:
            List[Case]: Список дел пользователя
        """
        pass

    @abstractmethod
    async def add_evidence(self, case_id: UUID, evidence: Evidence) -> None:
        """Добавляет улику к делу

        Args:
            case_id: ID дела
            evidence: Улика для добавления
        """
        pass

    @abstractmethod
    async def add_location(self, case_id: UUID, location: Location) -> None:
        """Добавляет локацию к делу

        Args:
            case_id: ID дела
            location: Локация для добавления
        """
        pass

    @abstractmethod
    async def add_suspect(self, case_id: UUID, suspect: Suspect) -> None:
        """Добавляет подозреваемого к делу

        Args:
            case_id: ID дела
            suspect: Подозреваемый для добавления
        """
        pass

    @abstractmethod
    async def get_evidence(
        self, case_id: UUID, evidence_id: UUID
    ) -> Optional[Evidence]:
        """Получает улику по ID

        Args:
            case_id: ID дела
            evidence_id: ID улики

        Returns:
            Optional[Evidence]: Найденная улика или None
        """
        pass

    @abstractmethod
    async def get_location(
        self, case_id: UUID, location_id: UUID
    ) -> Optional[Location]:
        """Получает локацию по ID

        Args:
            case_id: ID дела
            location_id: ID локации

        Returns:
            Optional[Location]: Найденная локация или None
        """
        pass

    @abstractmethod
    async def get_suspect(self, case_id: UUID, suspect_id: UUID) -> Optional[Suspect]:
        """Получает подозреваемого по ID

        Args:
            case_id: ID дела
            suspect_id: ID подозреваемого

        Returns:
            Optional[Suspect]: Найденный подозреваемый или None
        """
        pass
