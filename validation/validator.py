from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar
from datetime import datetime
import re
import uuid

from dark_archive.domain.validation.validation_error import (
    ValidationError,
    ValidationErrors,
    RequiredFieldError,
    InvalidValueError,
    InvalidFormatError,
)

T = TypeVar("T")


class Validator(ABC):
    """Base class for validators."""

    def __init__(self):
        self._errors: List[ValidationError] = []

    def validate(self, data: Any) -> None:
        """Validate data and raise ValidationErrors if any errors found."""
        self._errors = []
        self._validate(data)
        if self._errors:
            raise ValidationErrors(self._errors)

    @abstractmethod
    def _validate(self, data: Any) -> None:
        """Perform actual validation. Must be implemented by subclasses."""
        pass

    def add_error(self, error: ValidationError) -> None:
        """Add validation error."""
        self._errors.append(error)

    def validate_required(self, value: Any, field: str) -> None:
        """Validate that field value is not None or empty."""
        if value is None or (isinstance(value, (str, list, dict)) and not value):
            self.add_error(RequiredFieldError(field))

    def validate_string(
        self,
        value: Any,
        field: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
    ) -> None:
        """Validate string field."""
        if not isinstance(value, str):
            self.add_error(InvalidValueError(field, value, "Must be a string"))
            return

        if min_length is not None and len(value) < min_length:
            self.add_error(
                InvalidValueError(
                    field, value, f"Must be at least {min_length} characters long"
                )
            )

        if max_length is not None and len(value) > max_length:
            self.add_error(
                InvalidValueError(
                    field, value, f"Must be at most {max_length} characters long"
                )
            )

        if pattern is not None and not re.match(pattern, value):
            self.add_error(
                InvalidFormatError(field, value, f"Must match pattern: {pattern}")
            )

    def validate_number(
        self,
        value: Any,
        field: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        integer_only: bool = False,
    ) -> None:
        """Validate numeric field."""
        if not isinstance(value, (int, float)):
            self.add_error(InvalidValueError(field, value, "Must be a number"))
            return

        if integer_only and not isinstance(value, int):
            self.add_error(InvalidValueError(field, value, "Must be an integer"))
            return

        if min_value is not None and value < min_value:
            self.add_error(
                InvalidValueError(field, value, f"Must be at least {min_value}")
            )

        if max_value is not None and value > max_value:
            self.add_error(
                InvalidValueError(field, value, f"Must be at most {max_value}")
            )

    def validate_datetime(
        self,
        value: Any,
        field: str,
        min_date: Optional[datetime] = None,
        max_date: Optional[datetime] = None,
    ) -> None:
        """Validate datetime field."""
        if not isinstance(value, datetime):
            self.add_error(InvalidValueError(field, value, "Must be a datetime"))
            return

        if min_date is not None and value < min_date:
            self.add_error(InvalidValueError(field, value, f"Must be after {min_date}"))

        if max_date is not None and value > max_date:
            self.add_error(
                InvalidValueError(field, value, f"Must be before {max_date}")
            )

    def validate_uuid(self, value: Any, field: str) -> None:
        """Validate UUID field."""
        if not isinstance(value, uuid.UUID):
            try:
                uuid.UUID(str(value))
            except (ValueError, AttributeError, TypeError):
                self.add_error(InvalidValueError(field, value, "Must be a valid UUID"))

    def validate_list(
        self,
        value: Any,
        field: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        item_type: Optional[Type] = None,
    ) -> None:
        """Validate list field."""
        if not isinstance(value, list):
            self.add_error(InvalidValueError(field, value, "Must be a list"))
            return

        if min_length is not None and len(value) < min_length:
            self.add_error(
                InvalidValueError(
                    field, value, f"Must have at least {min_length} items"
                )
            )

        if max_length is not None and len(value) > max_length:
            self.add_error(
                InvalidValueError(field, value, f"Must have at most {max_length} items")
            )

        if item_type is not None:
            for i, item in enumerate(value):
                if not isinstance(item, item_type):
                    self.add_error(
                        InvalidValueError(
                            f"{field}[{i}]",
                            item,
                            f"Must be of type {item_type.__name__}",
                        )
                    )

    def validate_dict(
        self,
        value: Any,
        field: str,
        required_keys: Optional[List[str]] = None,
        optional_keys: Optional[List[str]] = None,
        value_type: Optional[Type] = None,
    ) -> None:
        """Validate dictionary field."""
        if not isinstance(value, dict):
            self.add_error(InvalidValueError(field, value, "Must be a dictionary"))
            return

        if required_keys:
            for key in required_keys:
                if key not in value:
                    self.add_error(RequiredFieldError(f"{field}.{key}"))

        allowed_keys = set(required_keys or []) | set(optional_keys or [])
        if allowed_keys:
            for key in value:
                if key not in allowed_keys:
                    self.add_error(
                        InvalidValueError(
                            field,
                            key,
                            f"Unknown key. Allowed keys: {sorted(allowed_keys)}",
                        )
                    )

        if value_type is not None:
            for key, val in value.items():
                if not isinstance(val, value_type):
                    self.add_error(
                        InvalidValueError(
                            f"{field}.{key}",
                            val,
                            f"Must be of type {value_type.__name__}",
                        )
                    )
