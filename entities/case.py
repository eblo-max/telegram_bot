"""Модуль, содержащий сущность Case (Дело)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

from dark_archive.domain.base_classes import BaseEntity
from dark_archive.domain.value_objects.message import MessageFormat
from dark_archive.utils.datetime_utils import get_current_time
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.entities.theory import Theory
from dark_archive.domain.enums import CaseStatus, CaseDifficulty


class CaseDifficulty(Enum):
    """Уровни сложности дела."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CaseStatus(Enum):
    """Статусы дела."""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
    CLOSED = "closed"
    ARCHIVED = "archived"


@dataclass
class Case(BaseEntity):
    """Класс, представляющий дело."""

    title: str
    description: str
    difficulty: CaseDifficulty
    status: CaseStatus = CaseStatus.NEW
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    solved_at: Optional[datetime] = None
    solution: Optional[str] = None
    evidence: List["Evidence"] = field(default_factory=list)
    locations: List["Location"] = field(default_factory=list)
    suspects: List["Suspect"] = field(default_factory=list)
    detective_notes: List[str] = field(default_factory=list)

    def __init__(
        self,
        title: str,
        description: str,
        difficulty: CaseDifficulty,
        id: Optional[UUID] = None,
        status: Optional[CaseStatus] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        solved_at: Optional[datetime] = None,
        solution: Optional[str] = None,
        evidence: Optional[List["Evidence"]] = None,
        locations: Optional[List["Location"]] = None,
        suspects: Optional[List["Suspect"]] = None,
        detective_notes: Optional[List[str]] = None,
    ):
        """Инициализация дела."""
        super().__init__(id)
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.status = status or CaseStatus.NEW
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.solved_at = solved_at
        self.solution = solution
        self.evidence = evidence or []
        self.locations = locations or []
        self.suspects = suspects or []
        self.detective_notes = detective_notes or []

    @property
    def id(self) -> UUID:
        """Получение ID дела."""
        return self._id

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        difficulty: CaseDifficulty,
        id: Optional[UUID] = None,
    ) -> "Case":
        """Создание нового дела."""
        return cls(
            title=title,
            description=description,
            difficulty=difficulty,
            id=id,
        )

    def add_evidence(self, evidence: "Evidence") -> None:
        """Добавление улики в дело."""
        evidence.case_id = self.id
        self.evidence.append(evidence)
        self.updated_at = datetime.utcnow()

    def add_location(self, location: "Location") -> None:
        """Добавление локации в дело."""
        location.case_id = self.id
        self.locations.append(location)
        self.updated_at = datetime.utcnow()

    def add_suspect(self, suspect: "Suspect") -> None:
        """Добавление подозреваемого в дело."""
        suspect.case_id = str(self.id)
        self.suspects.append(suspect)
        self.updated_at = datetime.utcnow()

    def solve(self, solution: str) -> None:
        """Завершение дела."""
        self.status = CaseStatus.SOLVED
        self.solution = solution
        self.solved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def calculate_progress(self) -> float:
        """Расчет прогресса расследования."""
        total_points = 0
        earned_points = 0

        # Очки за исследованные улики
        if self.evidence:
            total_points += len(self.evidence)
            earned_points += len([e for e in self.evidence if e.examined])

        # Очки за посещенные локации
        if self.locations:
            total_points += len(self.locations)
            earned_points += len([l for l in self.locations if l.visited])

        # Очки за допрошенных подозреваемых
        if self.suspects:
            total_points += len(self.suspects)
            earned_points += len(
                [s for s in self.suspects if s.interrogation_state == "interrogated"]
            )

        return earned_points / total_points if total_points > 0 else 0.0

    def add_note(self, note: str) -> None:
        """Добавляет заметку."""
        self.detective_notes.append(note)
        self.updated_at = datetime.utcnow()

    def update_status(self, status: CaseStatus) -> None:
        """Обновляет статус дела."""
        self.status = status
        self.updated_at = datetime.utcnow()

    def remove_evidence(self, evidence: "Evidence") -> None:
        """Удаляет улику."""
        self.evidence.remove(evidence)
        self.updated_at = datetime.utcnow()

    def remove_location(self, location: "Location") -> None:
        """Удаляет локацию."""
        self.locations.remove(location)
        self.updated_at = datetime.utcnow()

    def remove_suspect(self, suspect: "Suspect") -> None:
        """Удаляет подозреваемого."""
        self.suspects.remove(suspect)
        self.updated_at = datetime.utcnow()

    def clear_notes(self) -> None:
        """Очищает заметки."""
        self.detective_notes.clear()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование дела в словарь."""
        data = super().to_dict()
        data.update(
            {
                "title": self.title,
                "description": self.description,
                "difficulty": self.difficulty.value,
                "status": self.status.value,
                "detective_notes": self.detective_notes,
                "evidence": [evidence.to_dict() for evidence in self.evidence],
                "locations": [location.to_dict() for location in self.locations],
                "suspects": [suspect.to_dict() for suspect in self.suspects],
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Case":
        """Создает объект из словаря."""
        if "difficulty" in data:
            data["difficulty"] = CaseDifficulty(data["difficulty"])
        if "status" in data:
            data["status"] = CaseStatus(data["status"])
        if "solved_at" in data and data["solved_at"]:
            data["solved_at"] = datetime.fromisoformat(data["solved_at"])
        if "evidence" in data:
            data["evidence"] = [Evidence.from_dict(e) for e in data["evidence"]]
        if "locations" in data:
            data["locations"] = [Location.from_dict(l) for l in data["locations"]]
        if "suspects" in data:
            data["suspects"] = [Suspect.from_dict(s) for s in data["suspects"]]
        if "id" in data:
            del data["id"]  # ID будет создан базовым классом
        return cls(**data)

    def start_investigation(self) -> None:
        """Начинает расследование дела."""
        if self.is_investigation_started:
            raise ValueError("Investigation is already started")
        self.is_investigation_started = True
        self.investigation_started_at = datetime.now()
        self.status = "in_progress"

    def add_investigation_note(self, note: str) -> None:
        """Добавляет заметку к расследованию."""
        if not self.investigation_notes:
            self.investigation_notes = []
        self.investigation_notes.append(note)

    @property
    def solved(self) -> bool:
        """Проверяет, раскрыто ли дело."""
        return self.status == CaseStatus.SOLVED
