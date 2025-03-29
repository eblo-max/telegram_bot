from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List


class ValidationError(Exception):
    """Ошибка валидации значения."""

    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)


@dataclass(frozen=True)
class BaseValueObject(ABC):
    """Базовый класс для value objects с поддержкой валидации."""

    def __post_init__(self):
        """Выполняет валидацию после инициализации."""
        self.validate()

    @abstractmethod
    def validate(self) -> None:
        """Валидирует объект.

        Raises:
            ValidationError: если объект невалиден
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь."""
        return {
            key: value.to_dict() if isinstance(value, BaseValueObject) else value
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseValueObject":
        """Создает объект из словаря."""
        return cls(**data)
