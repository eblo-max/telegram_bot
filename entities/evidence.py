# Created by setup script

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from enum import Enum

from dark_archive.domain.entities.base import BaseEntity
from dark_archive.domain.enums import EvidenceType
from dark_archive.utils.datetime_utils import get_current_time


class EvidenceType(Enum):
    """Типы улик."""

    PHYSICAL = "physical"  # Физические улики
    DIGITAL = "digital"  # Цифровые улики
    DOCUMENT = "document"  # Документы
    TESTIMONY = "testimony"  # Показания
    TRACE = "trace"  # Следы
    OTHER = "other"  # Прочее


@dataclass
class Evidence(BaseEntity):
    """Класс, представляющий улику в деле."""

    case_id: UUID
    title: str
    description: str
    location: Optional[str] = None
    type: Optional[EvidenceType] = None
    examined: bool = False
    examination_notes: Optional[List[str]] = None
    relevance_score: Optional[float] = None
    discovered_at: Optional[datetime] = None
    related_suspect_ids: Optional[List[UUID]] = None

    def __init__(
        self,
        case_id: UUID,
        title: str,
        description: str,
        location: Optional[str] = None,
        type: Optional[EvidenceType] = None,
        id: UUID = None,
        examined: bool = False,
        examination_notes: Optional[List[str]] = None,
        relevance_score: Optional[float] = None,
        discovered_at: Optional[datetime] = None,
        related_suspect_ids: Optional[List[UUID]] = None,
    ):
        """Инициализация улики."""
        super().__init__(id)
        self.case_id = case_id
        self.title = title
        self.description = description
        self.location = location
        self.type = type
        self.examined = examined
        self.examination_notes = examination_notes or []
        self.relevance_score = relevance_score
        self.discovered_at = discovered_at or datetime.utcnow()
        self.related_suspect_ids = related_suspect_ids or []

    def __post_init__(self):
        if self.examination_notes is None:
            self.examination_notes = []

    def examine(self, notes: Optional[str] = None) -> None:
        """Examine the evidence and optionally add notes."""
        self.examined = True
        if notes:
            self.add_note(notes)

    def set_relevance_score(self, score: float) -> None:
        """Set the relevance score for the evidence."""
        if not 0 <= score <= 1:
            raise ValueError("Relevance score must be between 0 and 1")
        self.relevance_score = score

    @classmethod
    def create(
        cls,
        case_id: UUID,
        title: str,
        description: str,
        location: Optional[str] = None,
        type: Optional[EvidenceType] = None,
    ) -> "Evidence":
        """Create a new piece of evidence."""
        return cls(
            case_id=case_id,
            title=title,
            description=description,
            location=location,
            type=type,
            discovered_at=datetime.utcnow(),
        )

    @classmethod
    def discover(
        cls,
        case_id: UUID,
        title: str,
        description: str,
        location: str,
        type: EvidenceType,
    ) -> "Evidence":
        """Discover a new piece of evidence."""
        return cls.create(case_id, title, description, location, type)

    def add_note(self, note: str) -> None:
        """Add a note about the evidence examination."""
        if not note:
            raise ValueError("Note cannot be empty")
        self.examination_notes.append(note)

    def mark_as_examined(self) -> None:
        """Mark the evidence as examined."""
        self.examined = True

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование улики в словарь."""
        data = super().to_dict()
        data.update(
            {
                "title": self.title,
                "description": self.description,
                "case_id": str(self.case_id),
                "location": self.location,
                "type": self.type.value if self.type else None,
                "examined": self.examined,
                "examination_notes": self.examination_notes,
                "discovered_at": (
                    self.discovered_at.isoformat() if self.discovered_at else None
                ),
                "related_suspect_ids": [str(sid) for sid in self.related_suspect_ids],
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Evidence":
        """Создание улики из словаря."""
        if "case_id" in data:
            data["case_id"] = UUID(data["case_id"])
        if "type" in data:
            data["type"] = EvidenceType(data["type"])
        if "created_at" in data:
            del data["created_at"]  # Будет создано базовым классом
        if "updated_at" in data:
            del data["updated_at"]  # Будет создано базовым классом
        if "id" in data:
            del data["id"]  # ID будет создан базовым классом
        return cls(**data)

    def link_to_suspect(self, suspect_id: UUID) -> None:
        """Связывание улики с подозреваемым."""
        if suspect_id not in self.related_suspect_ids:
            self.related_suspect_ids.append(suspect_id)
