"""Базовые классы для сущностей."""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4


class BaseEntity:
    """Базовый класс для всех сущностей."""

    def __init__(self, id: Optional[UUID] = None):
        """Инициализация базового класса."""
        self._id = id or uuid4()
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

    @property
    def id(self) -> UUID:
        """Получение ID сущности."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Получение времени создания."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Получение времени последнего обновления."""
        return self._updated_at

    def _update_timestamp(self) -> None:
        """Обновление времени последнего изменения."""
        self._updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование базовой сущности в словарь."""
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def create(cls, data: Dict[str, Any]) -> "BaseEntity":
        """Создание сущности из словаря."""
        if "id" in data:
            data["id"] = UUID(data["id"])
        if "created_at" in data:
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)
