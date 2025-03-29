from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from dataclasses import dataclass


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
    photo_url: Optional[str] = None
    file_url: Optional[str] = None


class MessageService(ABC):
    """Базовый интерфейс для сервиса сообщений"""

    @abstractmethod
    async def send_message(self, chat_id: int, message: Message) -> Dict:
        """Отправляет сообщение пользователю

        Args:
            chat_id: ID чата
            message: Объект сообщения

        Returns:
            Dict: Результат отправки сообщения
        """
        pass

    @abstractmethod
    async def edit_message(
        self, chat_id: int, message_id: int, message: Message
    ) -> Dict:
        """Редактирует существующее сообщение

        Args:
            chat_id: ID чата
            message_id: ID сообщения
            message: Новое сообщение

        Returns:
            Dict: Результат редактирования сообщения
        """
        pass

    @abstractmethod
    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """Удаляет сообщение

        Args:
            chat_id: ID чата
            message_id: ID сообщения

        Returns:
            bool: True если сообщение успешно удалено
        """
        pass

    @abstractmethod
    async def send_photo(
        self, chat_id: int, photo_url: str, caption: Optional[str] = None
    ) -> Dict:
        """Отправляет фотографию

        Args:
            chat_id: ID чата
            photo_url: URL фотографии
            caption: Подпись к фотографии

        Returns:
            Dict: Результат отправки фотографии
        """
        pass

    @abstractmethod
    async def send_file(
        self, chat_id: int, file_url: str, caption: Optional[str] = None
    ) -> Dict:
        """Отправляет файл

        Args:
            chat_id: ID чата
            file_url: URL файла
            caption: Подпись к файлу

        Returns:
            Dict: Результат отправки файла
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
