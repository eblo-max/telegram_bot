# Created by setup script

from dataclasses import dataclass

from dark_archive.domain.value_objects.base_value_object import BaseValueObject


@dataclass(frozen=True)
class Reputation(BaseValueObject):
    """Репутация игрока в Dark Archive."""

    value: int

    def __post_init__(self):
        """Валидация значения репутации."""
        self.validate()

    def validate(self) -> None:
        """Валидирует значение репутации."""
        if not isinstance(self.value, int):
            raise ValueError("Reputation value must be an integer")
        if self.value < 0:
            raise ValueError("Reputation value cannot be negative")
