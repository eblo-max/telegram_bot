"""Сервис для работы с делами."""

from typing import List, Optional
from uuid import UUID

from dark_archive.domain.entities.case import Case
from dark_archive.domain.repositories.case_repository import CaseRepository


class CaseService:
    """Сервис для работы с делами."""

    def __init__(self, repository: CaseRepository):
        """Инициализация сервиса."""
        self._repository = repository

    def create_case(self, case: Case) -> Case:
        """Создание нового дела."""
        return self._repository.save(case)

    def get_case(self, case_id: UUID) -> Optional[Case]:
        """Получение дела по ID."""
        return self._repository.get(case_id)

    def get_all_cases(self) -> List[Case]:
        """Получение всех дел."""
        return self._repository.get_all()

    def update_case(self, case: Case) -> Case:
        """Обновление дела."""
        return self._repository.save(case)

    def delete_case(self, case_id: UUID) -> None:
        """Удаление дела."""
        self._repository.delete(case_id)
