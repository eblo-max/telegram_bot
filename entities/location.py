# Created by setup script

from typing import List, Optional, Set, Dict, Any
from uuid import UUID
from datetime import datetime

from dark_archive.domain.entities.base import BaseEntity
from dark_archive.domain.entities.evidence import Evidence


class Location(BaseEntity):
    """Класс, представляющий локацию."""

    def __init__(
        self,
        name: str,
        description: str,
        case_id: UUID,
        id: Optional[UUID] = None,
        visited: bool = False,
        visit_notes: Optional[List[str]] = None,
        evidence: Optional[List[Evidence]] = None,
        visited_at: Optional[datetime] = None,
        evidence_ids: Optional[Set[UUID]] = None,
    ):
        """Инициализация локации."""
        super().__init__(id)
        self.name = name
        self.description = description
        self.case_id = case_id
        self.visited = visited
        self.visit_notes = visit_notes or []
        self.evidence = evidence or []
        self.visited_at = visited_at
        self.evidence_ids = evidence_ids or set()

    def visit(self, notes: str) -> None:
        """Посещение локации."""
        self.visited = True
        self.visit_notes.append(notes)
        self.visited_at = datetime.utcnow()

    def add_evidence(self, evidence: Evidence) -> None:
        """Добавление улики в локацию."""
        self.evidence.append(evidence)
        self.evidence_ids.add(evidence.id)

    def remove_evidence(self, evidence: Evidence) -> None:
        """Удаление улики из локации."""
        self.evidence.remove(evidence)
        self.evidence_ids.remove(evidence.id)

    def mark_evidence_found(self, evidence: Evidence) -> None:
        """Отметка улики как найденной."""
        evidence.found = True

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование локации в словарь."""
        data = super().to_dict()
        data.update(
            {
                "name": self.name,
                "description": self.description,
                "case_id": str(self.case_id),
                "visited": self.visited,
                "visit_notes": self.visit_notes,
                "evidence": [evidence.to_dict() for evidence in self.evidence],
                "visited_at": self.visited_at.isoformat() if self.visited_at else None,
                "evidence_ids": [str(eid) for eid in self.evidence_ids],
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            }
        )
        return data

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        case_id: UUID,
        id: Optional[UUID] = None,
    ) -> "Location":
        """Создание новой локации."""
        return cls(
            name=name,
            description=description,
            case_id=case_id,
            id=id,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Location":
        """Создание локации из словаря."""
        if "case_id" in data:
            data["case_id"] = UUID(data["case_id"])
        if "evidence" in data:
            data["evidence"] = [Evidence.from_dict(e) for e in data["evidence"]]
        if "visited_at" in data and data["visited_at"]:
            data["visited_at"] = datetime.fromisoformat(data["visited_at"])
        if "evidence_ids" in data:
            data["evidence_ids"] = {UUID(eid) for eid in data["evidence_ids"]}
        if "created_at" in data:
            del data["created_at"]  # Будет создано базовым классом
        if "updated_at" in data:
            del data["updated_at"]  # Будет создано базовым классом
        if "id" in data:
            del data["id"]  # ID будет создан базовым классом
        return cls(**data)
