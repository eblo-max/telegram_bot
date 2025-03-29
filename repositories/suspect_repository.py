# Created by setup script

from abc import ABC, abstractmethod
from typing import Optional, List

from dark_archive.domain.entities.suspect import Suspect


class SuspectRepository(ABC):
    """Интерфейс репозитория для работы с подозреваемыми."""

    @abstractmethod
    async def get_by_id(self, suspect_id: str) -> Optional[Suspect]:
        """Получить подозреваемого по id."""
        pass

    @abstractmethod
    async def save(self, suspect: Suspect) -> None:
        """Сохранить подозреваемого."""
        pass

    @abstractmethod
    async def get_by_case_id(self, case_id: str) -> List[Suspect]:
        """Получить всех подозреваемых по id дела."""
        pass
