import logging
from typing import Dict, List, Optional
from uuid import UUID
from pathlib import Path

from dark_archive.application.interfaces.case_repository import ICaseRepository
from dark_archive.domain.models.case import Case, CaseStatus
from dark_archive.infrastructure.serialization.json_serializer import JsonSerializer
from dark_archive.application.interfaces.repository import Repository
from dark_archive.domain.entities.case import Case

logger = logging.getLogger(__name__)


class MemoryCaseRepository(Repository):
    """Реализация репозитория в памяти с возможностью сохранения состояния"""

    def __init__(self, storage_path: Optional[str] = None):
        self._cases: Dict[UUID, Case] = {}
        self._storage_path = storage_path
        self._serializer = JsonSerializer()

        if storage_path:
            self._storage_path = Path(storage_path)
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._load_state()

    def _save_state(self) -> None:
        """Сохраняет состояние в файл"""
        if not self._storage_path:
            return

        try:
            cases_data = {
                str(case_id): self._serializer.serialize(case)
                for case_id, case in self._cases.items()
            }
            self._serializer.save_to_file(cases_data, str(self._storage_path))
            logger.debug(f"State saved to {self._storage_path}")
        except Exception as e:
            logger.error(f"Failed to save state: {str(e)}")

    def _load_state(self) -> None:
        """Загружает состояние из файла"""
        if not self._storage_path:
            return

        try:
            cases_data = self._serializer.load_from_file(str(self._storage_path), dict)
            if cases_data:
                for case_id, case_data in cases_data.items():
                    self._cases[UUID(case_id)] = self._serializer.deserialize(
                        case_data, Case
                    )
            logger.debug(f"State loaded from {self._storage_path}")
        except Exception as e:
            logger.error(f"Failed to load state: {str(e)}")

    async def create(self, case: Case) -> None:
        """Создает новое дело"""
        self._cases[case.id] = case
        self._save_state()
        logger.debug(f"Created case {case.id}")

    async def get_by_id(self, case_id: UUID) -> Optional[Case]:
        """Получает дело по ID"""
        return self._cases.get(case_id)

    async def get_by_status(self, status: CaseStatus) -> List[Case]:
        """Получает список дел по статусу"""
        return [case for case in self._cases.values() if case.status == status]

    async def update(self, case: Case) -> None:
        """Обновляет существующее дело"""
        if case.id not in self._cases:
            raise ValueError(f"Case {case.id} not found")
        self._cases[case.id] = case
        self._save_state()
        logger.debug(f"Updated case {case.id}")

    async def delete(self, case_id: UUID) -> None:
        """Удаляет дело"""
        if case_id in self._cases:
            del self._cases[case_id]
            self._save_state()
            logger.debug(f"Deleted case {case_id}")
