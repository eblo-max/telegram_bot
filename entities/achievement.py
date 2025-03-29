# Created by setup script

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from dark_archive.domain.entities.base_entity import BaseEntity


@dataclass
class Achievement(BaseEntity):
    """Сущность достижения."""

    id: UUID = uuid4()
    name: str = ""
    description: str = ""
    category: str = ""
    points: int = 0
    requirements: Dict[str, int] = None  # Требования для получения достижения
    rewards: Dict[str, int] = None  # Награды за достижение
    icon: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Валидация после инициализации."""
        if self.requirements is None:
            self.requirements = {}
        if self.rewards is None:
            self.rewards = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

        if not self.name:
            raise ValueError("Название достижения не может быть пустым")
        if not self.description:
            raise ValueError("Описание достижения не может быть пустым")
        if not self.category:
            raise ValueError("Категория достижения не может быть пустой")
        if self.points < 0:
            raise ValueError("Очки достижения не могут быть отрицательными")
        if not self.requirements:
            raise ValueError("Достижение должно иметь хотя бы одно требование")
        if not self.rewards:
            raise ValueError("Достижение должно иметь хотя бы одну награду")

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        category: str,
        points: int,
        requirements: Dict[str, int],
        rewards: Dict[str, int],
        icon: Optional[str] = None,
    ) -> "Achievement":
        """Создает новое достижение."""
        return cls(
            id=uuid4(),
            name=name,
            description=description,
            category=category,
            points=points,
            requirements=requirements,
            rewards=rewards,
            icon=icon,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def update(self, **kwargs) -> None:
        """Обновляет данные достижения."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Преобразует достижение в словарь."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "points": self.points,
            "requirements": self.requirements,
            "rewards": self.rewards,
            "icon": self.icon,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Achievement":
        """Создает достижение из словаря."""
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            description=data["description"],
            category=data["category"],
            points=data["points"],
            requirements=data["requirements"],
            rewards=data["rewards"],
            icon=data.get("icon"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
