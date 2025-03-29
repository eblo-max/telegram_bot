from abc import ABC, abstractmethod
from typing import Dict, Any, Type, TypeVar, Optional
from datetime import datetime
from uuid import UUID, uuid4

from dark_archive.domain.validation.validator import Validator

T = TypeVar("T", bound="BaseEntity")


class BaseEntity(ABC):
    """Base class for domain entities with validation support."""

    def __init__(self):
        self._validator: Optional[Validator] = None

    @property
    @abstractmethod
    def id(self) -> UUID:
        """Get entity ID."""
        pass

    @property
    def created_at(self) -> datetime:
        """Get entity creation timestamp."""
        return getattr(self, "_created_at", datetime.utcnow())

    @property
    def updated_at(self) -> Optional[datetime]:
        """Get entity last update timestamp."""
        return getattr(self, "_updated_at", None)

    def validate(self) -> None:
        """Validate entity state."""
        if self._validator:
            self._validator.validate(self)

    def update(self) -> None:
        """Update entity timestamp."""
        self._updated_at = datetime.utcnow()

    @classmethod
    def _generate_id(cls) -> UUID:
        """Generate new UUID for entity."""
        return uuid4()

    @classmethod
    def create(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create entity from dictionary data."""
        instance = cls()
        instance.from_dict(data)
        instance.validate()
        return instance

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        pass

    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Update entity from dictionary data."""
        pass

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
