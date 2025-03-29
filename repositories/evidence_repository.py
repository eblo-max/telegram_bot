# Created by setup script

from typing import Optional
from uuid import UUID

from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.repositories.base_repository import BaseRepository


class EvidenceRepository(BaseRepository[Evidence]):
    """Репозиторий для работы с уликами."""

    async def get_by_id(self, id: UUID) -> Optional[Evidence]:
        """
        Получить улику по ID.

        Args:
            id: ID улики

        Returns:
            Evidence: Улика или None, если не найдена
        """
        pass

    async def save(self, entity: Evidence) -> Evidence:
        """
        Сохранить улику.

        Args:
            entity: Улика для сохранения

        Returns:
            Evidence: Сохраненная улика
        """
        pass

    async def delete(self, id: UUID) -> None:
        """
        Удалить улику.

        Args:
            id: ID улики
        """
        pass
