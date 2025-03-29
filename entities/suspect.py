# Created by setup script

from datetime import datetime, timedelta
from typing import List, Optional, Set, Dict, Any
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
from dark_archive.domain.entities.base import BaseEntity
from dark_archive.utils.datetime_utils import get_current_time
from dark_archive.domain.exceptions import SuspectInterrogationError
from dark_archive.domain.enums import SuspectStatus


class SuspectStatus(Enum):
    """Статусы подозреваемого."""

    UNKNOWN = "unknown"
    SUSPECT = "suspect"
    CLEARED = "cleared"
    GUILTY = "guilty"


@dataclass
class Suspect(BaseEntity):
    """Класс, представляющий подозреваемого."""

    name: str
    description: str
    case_id: UUID
    interrogation_state: str = field(default="not_interrogated")
    interrogation_cooldown_until: Optional[datetime] = None
    interrogation_notes: List[str] = field(default_factory=list)
    motives: List[str] = field(default_factory=list)
    alibi: Optional[str] = None
    notes: str = ""
    status: SuspectStatus = SuspectStatus.UNKNOWN
    evidence_ids: Set[UUID] = field(default_factory=set)
    risk_level: int = 0
    last_interrogated_at: Optional[datetime] = None

    def __init__(
        self,
        name: str,
        description: str,
        case_id: UUID,
        id: Optional[UUID] = None,
        status: Optional[SuspectStatus] = None,
        interrogation_cooldown_until: Optional[datetime] = None,
        last_interrogated_at: Optional[datetime] = None,
        interrogation_notes: Optional[List[str]] = None,
        evidence_ids: Optional[Set[UUID]] = None,
    ):
        """Инициализация подозреваемого."""
        super().__init__(id)
        self.name = name
        self.description = description
        self.case_id = case_id
        self.status = status or SuspectStatus.UNKNOWN
        self.interrogation_cooldown_until = interrogation_cooldown_until
        self.last_interrogated_at = last_interrogated_at
        self.interrogation_notes = interrogation_notes or []
        self.evidence_ids = evidence_ids or set()

    def can_be_interrogated(self) -> bool:
        """Проверяет, можно ли допросить подозреваемого."""
        if not self.interrogation_cooldown_until:
            return True
        return datetime.now() > self.interrogation_cooldown_until

    def interrogate(self, notes: str) -> None:
        """Допрос подозреваемого."""
        current_time = datetime.utcnow()

        if (
            self.interrogation_cooldown_until
            and current_time < self.interrogation_cooldown_until
        ):
            raise SuspectInterrogationError(
                f"Нельзя допрашивать подозреваемого до {self.interrogation_cooldown_until}"
            )

        self.interrogation_state = "interrogated"
        self.interrogation_notes.append(notes)
        self.interrogation_cooldown_until = current_time + timedelta(hours=24)

    def add_note(self, note: str) -> None:
        """Добавляет заметку о подозреваемом."""
        if not self.notes:
            self.notes = note
        else:
            self.notes = f"{self.notes}\n{note}"

    def set_alibi(self, alibi: str) -> None:
        """Устанавливает алиби подозреваемого."""
        self.alibi = alibi

    def add_motive(self, motive: str) -> None:
        """
        Добавляет мотив подозреваемого.

        Args:
            motive: Текст мотива
        """
        self.motives.append(motive)

    def set_motive(self, motive: str) -> None:
        """Устанавливает мотив подозреваемого."""
        self.motive = motive
        self.motives = [motive]

    def set_cooldown(self, hours: int = 24) -> None:
        """Устанавливает время ожидания до следующего допроса."""
        self.interrogation_cooldown_until = datetime.now() + timedelta(hours=hours)

    def add_interrogation_note(self, note: str) -> None:
        """Добавляет заметку о допросе."""
        self.interrogation_notes.append(note)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование подозреваемого в словарь."""
        data = super().to_dict()
        data.update(
            {
                "name": self.name,
                "description": self.description,
                "case_id": str(self.case_id),
                "status": self.status.value,
                "alibi": self.alibi,
                "interrogation_state": self.interrogation_state,
                "interrogation_notes": self.interrogation_notes,
                "interrogation_cooldown_until": self.interrogation_cooldown_until,
                "notes": self.notes,
                "motives": self.motives,
                "evidence_ids": list(self.evidence_ids),
                "risk_level": self.risk_level,
                "last_interrogated_at": (
                    self.last_interrogated_at.isoformat()
                    if self.last_interrogated_at
                    else None
                ),
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
    ) -> "Suspect":
        """Создание нового подозреваемого."""
        return cls(
            name=name,
            description=description,
            case_id=case_id,
            id=id,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Suspect":
        """Создает подозреваемого из словаря."""
        if "case_id" in data:
            data["case_id"] = UUID(data["case_id"])
        if "status" in data:
            data["status"] = SuspectStatus(data["status"])
        if (
            "interrogation_cooldown_until" in data
            and data["interrogation_cooldown_until"]
        ):
            data["interrogation_cooldown_until"] = datetime.fromisoformat(
                data["interrogation_cooldown_until"]
            )
        if "evidence_ids" in data:
            data["evidence_ids"] = {UUID(eid) for eid in data["evidence_ids"]}
        if "last_interrogated_at" in data and data["last_interrogated_at"]:
            data["last_interrogated_at"] = datetime.fromisoformat(
                data["last_interrogated_at"]
            )
        if "created_at" in data:
            del data["created_at"]  # Будет создано базовым классом
        if "updated_at" in data:
            del data["updated_at"]  # Будет создано базовым классом
        if "id" in data:
            del data["id"]  # ID будет создан базовым классом
        if "risk_level" in data:
            del data["risk_level"]  # Это поле больше не используется
        return cls(**data)

    def update_status(self, status: SuspectStatus) -> None:
        """Обновляет статус подозреваемого"""
        self.status = status

    def add_evidence(self, evidence_id: UUID) -> None:
        """Связывает улику с подозреваемым"""
        self.evidence_ids.add(evidence_id)
