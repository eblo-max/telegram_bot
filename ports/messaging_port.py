from abc import ABC, abstractmethod
from typing import Optional
from dark_archive.domain.interfaces.lifecycle_manager import ILifecycleManager
from dark_archive.domain.value_objects.message import OutboundMessage


class MessagingPort(ILifecycleManager, ABC):
    """Порт для отправки сообщений (Output Port)."""

    @abstractmethod
    async def send(self, message: OutboundMessage) -> None:
        """Отправляет сообщение через соответствующий канал.

        Args:
            message: Объект сообщения для отправки
        """
        pass

    @abstractmethod
    async def edit(self, message_id: str, message: OutboundMessage) -> None:
        """Редактирует существующее сообщение.

        Args:
            message_id: ID сообщения для редактирования
            message: Новое сообщение
        """
        pass

    @abstractmethod
    async def delete(self, recipient_id: str, message_id: str) -> bool:
        """Удаляет сообщение.

        Args:
            recipient_id: ID получателя
            message_id: ID сообщения для удаления

        Returns:
            bool: True если сообщение успешно удалено
        """
        pass

    @abstractmethod
    async def answer_callback(
        self, callback_id: str, text: Optional[str] = None
    ) -> None:
        """Отвечает на callback query.

        Args:
            callback_id: ID callback query
            text: Текст ответа
        """
        pass
