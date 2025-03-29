from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable

from dark_archive.domain.value_objects.message import OutboundMessage


class ITelegramClient(ABC):
    """Интерфейс для работы с Telegram API"""

    @abstractmethod
    async def initialize(self) -> None:
        """Инициализация клиента"""
        pass

    @abstractmethod
    async def add_handler(self, handler: Callable) -> None:
        """Добавляет обработчик команды

        Args:
            handler: Функция-обработчик
        """
        pass

    @abstractmethod
    def add_callback_query_handler(self, handler: Callable) -> None:
        """Добавляет обработчик callback query

        Args:
            handler: Асинхронная функция-обработчик
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """Запускает бота"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Останавливает бота"""
        pass

    @abstractmethod
    async def send_message(self, chat_id: int, message: OutboundMessage) -> None:
        """Отправляет сообщение

        Args:
            chat_id: ID чата
            message: Сообщение для отправки
        """
        pass

    @abstractmethod
    async def edit_message(
        self, chat_id: int, message_id: int, message: OutboundMessage
    ) -> None:
        """Редактирует сообщение

        Args:
            chat_id: ID чата
            message_id: ID сообщения
            message: Новое сообщение
        """
        pass

    @abstractmethod
    async def answer_callback(
        self, callback_id: str, text: Optional[str] = None
    ) -> None:
        """Отвечает на callback query

        Args:
            callback_id: ID callback query
            text: Текст уведомления
        """
        pass
