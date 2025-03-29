from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from dark_archive.domain.interfaces.command_handler import (
    CommandHandler,
    CommandContext,
)
from dark_archive.domain.interfaces.state_handler import (
    StateHandler,
    StateContext,
    State,
)
from dark_archive.domain.interfaces.callback_handler import (
    CallbackHandler,
    CallbackContext,
)
from dark_archive.domain.interfaces.message_service import MessageService
from dark_archive.domain.interfaces.message_formatter import MessageFormatter
from dark_archive.domain.services.case_service import CaseService


class BaseBotHandler(CommandHandler, StateHandler, CallbackHandler):
    """Базовый класс для обработчиков команд бота"""

    def __init__(
        self,
        case_service: CaseService,
        message_service: MessageService,
        message_formatter: MessageFormatter,
        commands: List[str],
        states: List[State],
        callback_prefixes: List[str],
    ):
        self._case_service = case_service
        self._message_service = message_service
        self._message_formatter = message_formatter
        self._commands = commands
        self._states = states
        self._callback_prefixes = callback_prefixes

    async def can_handle_command(self, command: str) -> bool:
        """Проверяет, может ли обработчик обработать команду"""
        return command in self._commands

    async def can_handle_state(self, state: State) -> bool:
        """Проверяет, может ли обработчик обработать состояние"""
        return state in self._states

    async def can_handle_callback(self, data: str) -> bool:
        """Проверяет, может ли обработчик обработать callback"""
        prefix = data.split(":")[0] if ":" in data else data
        return prefix in self._callback_prefixes

    @abstractmethod
    async def handle_command(self, context: CommandContext) -> None:
        """Обрабатывает команду

        Args:
            context: Контекст команды
        """
        pass

    @abstractmethod
    async def handle_state(self, context: StateContext) -> None:
        """Обрабатывает состояние

        Args:
            context: Контекст состояния
        """
        pass

    @abstractmethod
    async def handle_callback(self, context: CallbackContext) -> None:
        """Обрабатывает callback

        Args:
            context: Контекст callback-запроса
        """
        pass

    async def send_error(self, chat_id: int, error: str) -> None:
        """Отправляет сообщение об ошибке

        Args:
            chat_id: ID чата
            error: Текст ошибки
        """
        message = self._message_formatter.format_error(error)
        await self._message_service.send_message(chat_id, message)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        keyboard: Optional[List[List[Dict[str, str]]]] = None,
    ) -> None:
        """Отправляет сообщение

        Args:
            chat_id: ID чата
            text: Текст сообщения
            keyboard: Клавиатура
        """
        await self._message_service.send_message(
            chat_id, self._message_formatter.format_message(text, keyboard)
        )

    async def edit_message(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        keyboard: Optional[List[List[Dict[str, str]]]] = None,
    ) -> None:
        """Редактирует сообщение

        Args:
            chat_id: ID чата
            message_id: ID сообщения
            text: Новый текст
            keyboard: Новая клавиатура
        """
        await self._message_service.edit_message(
            chat_id, message_id, self._message_formatter.format_message(text, keyboard)
        )

    async def answer_callback(
        self, callback_id: str, text: Optional[str] = None
    ) -> None:
        """Отвечает на callback

        Args:
            callback_id: ID callback-запроса
            text: Текст уведомления
        """
        await self._message_service.answer_callback(callback_id, text)
