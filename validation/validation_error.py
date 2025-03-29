from typing import Dict, Any, Optional


class ValidationError(Exception):
    """Base class for validation errors."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        details: Optional[Dict] = None,
    ):
        self.message = message
        self.field = field
        self.value = value
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.field:
            return f"{self.field}: {self.message}"
        return self.message

    def to_dict(self) -> Dict:
        """Convert validation error to dictionary."""
        return {
            "message": self.message,
            "field": self.field,
            "value": str(self.value) if self.value is not None else None,
            "details": self.details,
        }


class RequiredFieldError(ValidationError):
    """Error raised when a required field is missing."""

    def __init__(self, field: str):
        super().__init__(message=f"Field '{field}' is required", field=field)


class InvalidValueError(ValidationError):
    """Error raised when a field value is invalid."""

    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            message=f"Invalid value for field '{field}': {reason}",
            field=field,
            value=value,
            details={"reason": reason},
        )


class InvalidFormatError(ValidationError):
    """Error raised when a field value has invalid format."""

    def __init__(self, field: str, value: Any, expected_format: str):
        super().__init__(
            message=f"Invalid format for field '{field}', expected {expected_format}",
            field=field,
            value=value,
            details={"expected_format": expected_format},
        )


class ValidationErrors(Exception):
    """Container for multiple validation errors."""

    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
        messages = [str(error) for error in errors]
        super().__init__("\n".join(messages))

    def to_dict(self) -> Dict:
        """Convert validation errors to dictionary."""
        return {"errors": [error.to_dict() for error in self.errors]}
