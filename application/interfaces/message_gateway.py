from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from dark_archive.domain.interfaces.lifecycle_manager import ILifecycleManager
from dark_archive.domain.value_objects.message import Message, Button


@dataclass
class Button:
    """Кнопка для интерактивной клавиатуры"""

    text: str
    callback_data: str


@dataclass
class Message:
    """Сообщение для отправки"""

    text: str
    keyboard_buttons: Optional[List[List[Button]]] = None
    parse_mode: Optional[str] = None


class IMessageGateway(ILifecycleManager, ABC):
    """Интерфейс для отправки сообщений"""

    @abstractmethod
    async def send_message(self, chat_id: str, message: Message) -> None:
        """Отправляет сообщение пользователю

        Args:
            chat_id: ID чата
            message: Объект сообщения с текстом и кнопками
        """
        pass

    @abstractmethod
    async def edit_message(
        self, chat_id: str, message_id: str, message: Message
    ) -> None:
        """Редактирует существующее сообщение

        Args:
            chat_id: ID чата
            message_id: ID сообщения для редактирования
            message: Новое сообщение
        """
        pass

    @abstractmethod
    async def delete_message(self, chat_id: str, message_id: str) -> bool:
        """Удаляет сообщение"""
        pass

    @abstractmethod
    async def answer_callback(
        self, callback_id: str, text: Optional[str] = None
    ) -> None:
        """Отвечает на callback query

        Args:
            callback_id: ID callback query
            text: Текст всплывающего уведомления
        """
        pass
