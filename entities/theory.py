from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from dark_archive.domain.base_classes import BaseEntity


@dataclass
class Theory(BaseEntity):
    """Класс теории."""

    case_id: str
    description: str
    evidence_ids: List[str] = field(default_factory=list)
    suspect_ids: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def __init__(
        self,
        id: str,
        case_id: str,
        description: str,
        evidence_ids: List[str] = None,
        suspect_ids: List[str] = None,
        notes: List[str] = None,
        created_at: Optional[datetime] = None,
    ):
        """Инициализирует теорию."""
        super().__init__(id)
        self.case_id = case_id
        self.description = description
        self.evidence_ids = evidence_ids or []
        self.suspect_ids = suspect_ids or []
        self.notes = notes or []
        self.created_at = created_at or datetime.now()

    @classmethod
    def create(cls, case_id: str, description: str) -> "Theory":
        """Создает новую теорию."""
        return cls(
            id=str(uuid4()),
            case_id=case_id,
            description=description,
            evidence_ids=[],
            suspect_ids=[],
            notes=[],
            created_at=datetime.now(),
        )

    def add_evidence(self, evidence_id: str) -> None:
        """Добавляет улику."""
        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)

    def add_suspect(self, suspect_id: str) -> None:
        """Добавляет подозреваемого."""
        if suspect_id not in self.suspect_ids:
            self.suspect_ids.append(suspect_id)

    def add_note(self, note: str) -> None:
        """Добавляет заметку."""
        self.notes.append(note)

    def remove_evidence(self, evidence_id: str) -> None:
        """Удаляет улику."""
        if evidence_id in self.evidence_ids:
            self.evidence_ids.remove(evidence_id)

    def remove_suspect(self, suspect_id: str) -> None:
        """Удаляет подозреваемого."""
        if suspect_id in self.suspect_ids:
            self.suspect_ids.remove(suspect_id)

    def clear_notes(self) -> None:
        """Очищает заметки."""
        self.notes.clear()

    def to_dict(self) -> dict:
        """Преобразует объект в словарь."""
        return {
            "id": str(self.id),
            "case_id": self.case_id,
            "description": self.description,
            "evidence_ids": self.evidence_ids,
            "suspect_ids": self.suspect_ids,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Theory":
        """Создает объект из словаря."""
        return cls(
            id=data["id"],
            case_id=data["case_id"],
            description=data["description"],
            evidence_ids=data["evidence_ids"],
            suspect_ids=data["suspect_ids"],
            notes=data["notes"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )
