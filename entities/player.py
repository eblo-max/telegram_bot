# Created by setup script

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
import time

from dark_archive.domain.entities.base import BaseEntity
from dark_archive.domain.value_objects.reputation import Reputation
from dark_archive.domain.enums import PlayerRole
from dark_archive.domain.entities.case import Case
from dark_archive.domain.exceptions import AccessDeniedError


class Player(BaseEntity):
    """Класс, представляющий игрока."""

    def __init__(
        self,
        username: str,
        role: PlayerRole,
        telegram_id: int,
        id: Optional[UUID] = None,
        active_case_id: Optional[UUID] = None,
        solved_cases: Optional[List[UUID]] = None,
        last_active: Optional[datetime] = None,
    ):
        """Инициализация игрока."""
        super().__init__(id)
        self._username = username
        self._role = role
        self._telegram_id = telegram_id
        self._active_case_id = active_case_id
        self._solved_cases = solved_cases or []
        self._last_active = last_active or datetime.utcnow()

    @property
    def username(self) -> str:
        """Получение имени пользователя."""
        return self._username

    @property
    def role(self) -> PlayerRole:
        """Получение роли игрока."""
        return self._role

    @property
    def telegram_id(self) -> int:
        """Получение ID в Telegram."""
        return self._telegram_id

    @property
    def active_case_id(self) -> Optional[UUID]:
        """Получение ID активного дела."""
        return self._active_case_id

    @active_case_id.setter
    def active_case_id(self, value: Optional[UUID]) -> None:
        """Установка ID активного дела."""
        self._active_case_id = value

    @property
    def solved_cases(self) -> List[UUID]:
        """Получение списка решенных дел."""
        return self._solved_cases

    @property
    def last_active(self) -> datetime:
        """Получение времени последней активности."""
        return self._last_active

    @last_active.setter
    def last_active(self, value: datetime) -> None:
        """Установка времени последней активности."""
        self._last_active = value

    def has_access_to_case(self, case: Case) -> bool:
        """
        Проверяет, имеет ли игрок доступ к делу.

        Args:
            case: Дело для проверки

        Returns:
            True, если игрок имеет доступ к делу, иначе False
        """
        if self.role == PlayerRole.ADMIN:
            return True
        if self.role == PlayerRole.DETECTIVE:
            return self.active_case_id == case.id or case.id in self.solved_cases
        return False

    def assign_case(self, case_id: UUID) -> None:
        """
        Назначает игроку дело.

        Args:
            case_id: ID дела
        """
        self.active_case_id = case_id
        self._update_timestamp()

    def complete_case(self, case_id: str) -> None:
        """
        Отмечает дело как завершенное.

        Args:
            case_id: ID дела
        """
        if case_id == self.active_case_id:
            self.active_case_id = None
        self.solved_cases.append(UUID(case_id))

    def update_last_active(self) -> None:
        """Обновляет время последней активности."""
        old_time = self.last_active
        while True:
            self.last_active = datetime.now()
            self.last_activity = self.last_active  # Для совместимости со старым кодом
            if self.last_active > old_time:
                break
            time.sleep(0.001)

    def has_active_case(self) -> bool:
        """
        Проверяет, есть ли у игрока активное дело.

        Returns:
            True, если у игрока есть активное дело, иначе False
        """
        return self.active_case_id is not None

    def has_solved_case(self, case_id: str) -> bool:
        """
        Проверяет, решил ли игрок указанное дело.

        Args:
            case_id: ID дела

        Returns:
            True, если игрок решил дело, иначе False
        """
        return case_id in self.solved_cases

    def change_role(self, new_role: PlayerRole) -> None:
        """
        Изменяет роль игрока.

        Args:
            new_role: Новая роль
        """
        self._role = new_role

    def clear_active_case(self) -> None:
        """Очищает активное дело."""
        self.active_case_id = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование игрока в словарь."""
        data = super().to_dict()
        data.update(
            {
                "username": self.username,
                "role": self.role.value,
                "telegram_id": self.telegram_id,
                "active_case_id": (
                    str(self.active_case_id) if self.active_case_id else None
                ),
                "solved_cases": [str(case_id) for case_id in self.solved_cases],
                "last_active": self.last_active.isoformat(),
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Создание игрока из словаря."""
        if "role" in data:
            data["role"] = PlayerRole(data["role"])
        if "active_case_id" in data and data["active_case_id"]:
            data["active_case_id"] = UUID(data["active_case_id"])
        if "solved_cases" in data:
            data["solved_cases"] = [UUID(case_id) for case_id in data["solved_cases"]]
        if "last_active" in data:
            data["last_active"] = datetime.fromisoformat(data["last_active"])
        if "created_at" in data:
            del data["created_at"]  # Будет создано базовым классом
        if "updated_at" in data:
            del data["updated_at"]  # Будет создано базовым классом
        if "id" in data:
            del data["id"]  # ID будет создан базовым классом
        return cls(**data)

    def update_reputation(self, value: int) -> None:
        """Обновляет репутацию игрока."""
        self.reputation = Reputation(self.reputation.value + value)

    def add_achievement(self, achievement_id: str) -> None:
        """Добавляет достижение игроку."""
        if achievement_id not in self.achievements:
            self.achievements[achievement_id] = datetime.now()

    def has_achievement(self, achievement_id: str) -> bool:
        """Проверяет наличие достижения у игрока."""
        return achievement_id in self.achievements

    def start_case(self, case_id: UUID) -> None:
        """Начинает новое расследование."""
        self.active_case_id = case_id
        self.last_activity = datetime.now()

    def collect_evidence(self) -> None:
        """Увеличивает счетчик собранных улик."""
        self.evidence_collected += 1
        self.last_activity = datetime.now()

    def submit_theory(self) -> None:
        """Увеличивает счетчик предложенных теорий."""
        self.theories_submitted += 1
        self.last_activity = datetime.now()

    def is_active(self, timeout_minutes: int = 30) -> bool:
        """Проверяет, активен ли игрок."""
        if not self.last_activity:
            return False
        delta = datetime.now() - self.last_activity
        return delta.total_seconds() < timeout_minutes * 60

    def increment_active_investigations(self) -> None:
        """Увеличивает счетчик активных расследований."""
        self.active_investigations_count += 1

    @classmethod
    def create(
        cls,
        username: str,
        role: PlayerRole,
        telegram_id: int,
        id: Optional[UUID] = None,
    ) -> "Player":
        """Создание нового игрока."""
        return cls(
            username=username,
            role=role,
            telegram_id=telegram_id,
            id=id,
        )
