# Created by setup script

from typing import Optional, Dict, Any, Callable
from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)


class UpdateHandler:
    """Обработчик обновлений от Telegram"""

    def __init__(self):
        self._command_handlers: Dict[str, Callable] = {}
        self._callback_handlers: Dict[str, Callable] = {}

    async def handle_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка команд

        Args:
            update: Объект обновления от Telegram
            context: Контекст обработчика
        """
        if not update.message or not update.message.text:
            return

        command = update.message.text.split()[0].replace("/", "")
        if command in self._command_handlers:
            try:
                await self._command_handlers[command](update, context)
            except Exception as e:
                logger.error(f"Ошибка при обработке команды {command}: {str(e)}")

    async def handle_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработка callback запросов

        Args:
            update: Объект обновления от Telegram
            context: Контекст обработчика
        """
        if not update.callback_query or not update.callback_query.data:
            return

        callback_data = update.callback_query.data
        if callback_data in self._callback_handlers:
            try:
                await self._callback_handlers[callback_data](update, context)
            except Exception as e:
                logger.error(f"Ошибка при обработке callback {callback_data}: {str(e)}")

    def add_command_handler(self, command: str, handler: Callable) -> None:
        """Добавление обработчика команды

        Args:
            command: Команда без символа '/'
            handler: Функция-обработчик
        """
        self._command_handlers[command] = handler

    def add_callback_handler(self, callback_data: str, handler: Callable) -> None:
        """Добавление обработчика callback запроса

        Args:
            callback_data: Данные callback запроса
            handler: Функция-обработчик
        """
        self._callback_handlers[callback_data] = handler
