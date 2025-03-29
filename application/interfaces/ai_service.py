# Created by setup script

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from uuid import UUID
from dark_archive.application.dto.case_dto import CaseDTO, EvidenceDTO, SuspectDTO
from dark_archive.domain.models.case import Case, Evidence, Location


class IAIService(ABC):
    """Интерфейс для работы с AI сервисом"""

    @abstractmethod
    async def generate_case(self, difficulty: int) -> Dict:
        """
        Генерирует новое расследование заданной сложности

        Args:
            difficulty: Сложность расследования (1-10)

        Returns:
            Dict с деталями расследования:
            {
                "title": str,
                "description": str,
                "initial_location": {
                    "name": str,
                    "description": str,
                    "risk_level": int
                },
                "locations": [
                    {
                        "name": str,
                        "description": str,
                        "risk_level": int,
                        "evidence": [
                            {
                                "name": str,
                                "description": str,
                                "type": str,
                                "importance": int
                            }
                        ]
                    }
                ]
            }
        """
        pass

    @abstractmethod
    async def analyze_evidence(
        self, case: Case, evidence: Evidence, context: Optional[Dict[str, str]] = None
    ) -> str:
        """Анализирует улику и предоставляет выводы

        Args:
            case: Текущее дело
            evidence: Улика для анализа
            context: Дополнительный контекст

        Returns:
            str: Результаты анализа
        """
        pass

    @abstractmethod
    async def generate_location_description(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует описание локации с учетом найденных улик

        Args:
            case: Текущее дело
            location: Локация для описания
            discovered_evidence: Найденные улики в локации

        Returns:
            str: Описание локации
        """
        pass

    @abstractmethod
    async def evaluate_theory(
        self, case: Case, theory: str, evidence_ids: List[UUID]
    ) -> Dict[str, float]:
        """Оценивает теорию игрока

        Args:
            case: Текущее дело
            theory: Теория игрока
            evidence_ids: Список ID улик, использованных в теории

        Returns:
            Dict[str, float]: Оценка теории (точность, полнота, связность)
        """
        pass

    @abstractmethod
    async def generate_hint(
        self, case: Case, current_progress: float, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует подсказку для игрока

        Args:
            case: Текущее дело
            current_progress: Текущий прогресс расследования (0-1)
            discovered_evidence: Список найденных улик

        Returns:
            str: Подсказка для игрока
        """
        pass
