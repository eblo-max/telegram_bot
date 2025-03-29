from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CallbackContext:
    """Контекст callback-запроса"""

    user_id: int
    chat_id: int
    message_id: int
    callback_id: str
    data: str
    state_data: Optional[Dict[str, Any]] = None


class CallbackHandler(ABC):
    """Базовый интерфейс для обработчиков callback-запросов"""

    @abstractmethod
    async def handle(self, context: CallbackContext) -> None:
        """Обрабатывает callback-запрос

        Args:
            context: Контекст callback-запроса
        """
        pass

    @abstractmethod
    async def can_handle(self, data: str) -> bool:
        """Проверяет, может ли обработчик обработать callback-запрос

        Args:
            data: Данные callback-запроса

        Returns:
            bool: True если обработчик может обработать callback-запрос
        """
        pass


class CallbackDispatcher:
    """Диспетчер callback-запросов"""

    def __init__(self):
        self._handlers: Dict[str, CallbackHandler] = {}

    def register_handler(self, prefix: str, handler: CallbackHandler) -> None:
        """Регистрирует обработчик для callback-запросов с определенным префиксом

        Args:
            prefix: Префикс callback-данных
            handler: Обработчик callback-запросов
        """
        self._handlers[prefix] = handler

    async def dispatch(self, context: CallbackContext) -> None:
        """Диспетчеризует callback-запрос соответствующему обработчику

        Args:
            context: Контекст callback-запроса

        Raises:
            ValueError: Если обработчик для callback-запроса не найден
        """
        # Ищем обработчик по префиксу данных
        prefix = context.data.split(":")[0] if ":" in context.data else context.data
        handler = self._handlers.get(prefix)

        if not handler:
            raise ValueError(
                f"Обработчик для callback-запроса с префиксом {prefix} не найден"
            )

        if await handler.can_handle(context.data):
            await handler.handle(context)
        else:
            raise ValueError(
                f"Обработчик {handler.__class__.__name__} не может обработать callback-запрос {context.data}"
            )


class BaseCallbackHandler(CallbackHandler):
    """Базовый класс для обработчиков callback-запросов"""

    def __init__(self, prefixes: list[str]):
        self._prefixes = prefixes

    async def can_handle(self, data: str) -> bool:
        """Проверяет, может ли обработчик обработать callback-запрос"""
        prefix = data.split(":")[0] if ":" in data else data
        return prefix in self._prefixes
