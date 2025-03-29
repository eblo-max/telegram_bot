from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
from enum import Enum
from uuid import UUID, uuid4


class CaseStatus(Enum):
    """Статус расследования"""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
    CLOSED = "closed"


class EvidenceType(Enum):
    """Тип улики"""

    PHYSICAL = "physical"  # Физические улики
    DIGITAL = "digital"  # Цифровые улики
    FORENSIC = "forensic"  # Криминалистические улики
    WITNESS = "witness"  # Показания свидетелей
    OCCULT = "occult"  # Оккультные улики


@dataclass
class Evidence:
    """Улика в расследовании"""

    id: UUID
    name: str
    description: str
    type: str  # document, item, trace, record
    importance: int  # 1-10
    is_discovered: bool = False


@dataclass
class Location:
    """Локация в расследовании"""

    id: UUID
    name: str
    description: str
    risk_level: int  # 1-10
    evidence: List[Evidence]
    is_available: bool = True  # Доступность локации по умолчанию


@dataclass
class Case:
    """Расследование"""

    id: UUID
    title: str
    description: str
    status: str  # active, completed, failed
    difficulty: int
    created_at: datetime
    initial_location: Location
    locations: List[Location]
    current_location: Location
    discovered_evidence: List[Evidence]
    progress: float  # 0.0 - 1.0

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        difficulty: int,
        initial_location: Location,
    ) -> "Case":
        """Создает новое расследование"""
        return cls(
            id=uuid4(),
            title=title,
            description=description,
            status=CaseStatus.NEW.value,
            difficulty=difficulty,
            created_at=datetime.now(),
            initial_location=initial_location,
            locations=[initial_location],
            current_location=initial_location,
            discovered_evidence=[],
            progress=0.0,
        )

    def add_evidence(self, evidence: Evidence) -> None:
        """Добавляет улику к делу"""
        self.discovered_evidence.append(evidence)

    def add_location(self, location: Location) -> None:
        """Добавляет локацию к делу"""
        self.locations.append(location)

    def update_status(self, new_status: CaseStatus) -> None:
        """Обновляет статус расследования"""
        self.status = new_status.value

    def link_case(self, related_case_id: UUID) -> None:
        """Связывает дело с другим расследованием"""
        # Implementation needed
