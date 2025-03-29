from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CommandContext:
    """Контекст выполнения команды"""

    user_id: int
    chat_id: int
    command: str
    args: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class CommandHandler(ABC):
    """Базовый интерфейс для обработчиков команд"""

    @abstractmethod
    async def handle(self, context: CommandContext) -> None:
        """Обрабатывает команду

        Args:
            context: Контекст выполнения команды
        """
        pass

    @abstractmethod
    async def can_handle(self, command: str) -> bool:
        """Проверяет, может ли обработчик обработать команду

        Args:
            command: Команда для проверки

        Returns:
            bool: True если обработчик может обработать команду
        """
        pass


class CommandDispatcher:
    """Диспетчер команд"""

    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}

    def register_handler(self, command: str, handler: CommandHandler) -> None:
        """Регистрирует обработчик для команды

        Args:
            command: Команда
            handler: Обработчик команды
        """
        self._handlers[command] = handler

    async def dispatch(self, context: CommandContext) -> None:
        """Диспетчеризует команду соответствующему обработчику

        Args:
            context: Контекст выполнения команды

        Raises:
            ValueError: Если обработчик для команды не найден
        """
        handler = self._handlers.get(context.command)
        if not handler:
            raise ValueError(f"Обработчик для команды {context.command} не найден")

        if await handler.can_handle(context.command):
            await handler.handle(context)
        else:
            raise ValueError(
                f"Обработчик {handler.__class__.__name__} не может обработать команду {context.command}"
            )


class BaseCommandHandler(CommandHandler):
    """Базовый класс для обработчиков команд"""

    def __init__(self, commands: list[str]):
        self._commands = commands

    async def can_handle(self, command: str) -> bool:
        """Проверяет, может ли обработчик обработать команду"""
        return command in self._commands
