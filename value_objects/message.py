from dataclasses import dataclass
from typing import Optional, List

from dark_archive.domain.value_objects.base_value_object import (
    BaseValueObject,
    ValidationError,
)


@dataclass(frozen=True)
class MessageFormat:
    """Value Object для форматирования сообщений."""

    MARKDOWN = "Markdown"
    HTML = "HTML"
    PLAIN = None


@dataclass(frozen=True)
class Button(BaseValueObject):
    """Кнопка для интерактивной клавиатуры."""

    text: str
    callback_data: str

    def validate(self) -> None:
        """Валидирует кнопку."""
        if not self.text:
            raise ValidationError("Button text cannot be empty", "text")
        if not self.callback_data:
            raise ValidationError(
                "Button callback_data cannot be empty", "callback_data"
            )
        if len(self.text) > 100:
            raise ValidationError("Button text too long (max 100 chars)", "text")
        if len(self.callback_data) > 64:
            raise ValidationError(
                "Button callback_data too long (max 64 chars)", "callback_data"
            )

    def to_dict(self) -> dict:
        """Преобразует кнопку в словарь."""
        return {
            "text": self.text,
            "callback_data": self.callback_data,
        }


@dataclass(frozen=True)
class OutboundMessage:
    """Value Object для исходящих сообщений."""

    recipient_id: str
    content: str
    format: Optional[str] = None
    keyboard_buttons: Optional[List[List[Button]]] = None


@dataclass(frozen=True)
class Message(BaseValueObject):
    """Сообщение для отправки."""

    text: str
    keyboard_buttons: Optional[List[List[Button]]] = None
    parse_mode: Optional[str] = None
    photo_url: Optional[str] = None
    file_url: Optional[str] = None

    def validate(self) -> None:
        """Валидирует сообщение."""
        if not self.text:
            raise ValidationError("Message text cannot be empty", "text")
        if len(self.text) > 4096:
            raise ValidationError("Message text too long (max 4096 chars)", "text")

        if self.parse_mode and self.parse_mode not in ["Markdown", "HTML"]:
            raise ValidationError(
                "Invalid parse_mode. Must be 'Markdown' or 'HTML'", "parse_mode"
            )

        if self.keyboard_buttons:
            if len(self.keyboard_buttons) > 10:
                raise ValidationError(
                    "Too many keyboard rows (max 10)", "keyboard_buttons"
                )
            for row in self.keyboard_buttons:
                if len(row) > 8:
                    raise ValidationError(
                        "Too many buttons in row (max 8)", "keyboard_buttons"
                    )

        if self.photo_url and self.file_url:
            raise ValidationError(
                "Cannot have both photo_url and file_url", "photo_url"
            )
