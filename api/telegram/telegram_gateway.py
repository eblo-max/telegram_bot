import logging
from typing import Optional, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from dark_archive.domain.ports.messaging_port import MessagingPort
from dark_archive.domain.value_objects.message import (
    OutboundMessage,
    Button,
    Message,
)
from dark_archive.infrastructure.api.telegram.bot_client import (
    TelegramClientAdapter,
)


class TelegramGateway(MessagingPort):
    """Адаптер для отправки сообщений через Telegram"""

    def __init__(self, client: TelegramClientAdapter):
        self._client = client
        self._logger = logging.getLogger(__name__)
        self._initialized = False

    async def initialize(self) -> bool:
        """Инициализирует шлюз."""
        try:
            self._initialized = True
            self._logger.info("TelegramGateway initialized successfully")
            return True
        except Exception as e:
            self._logger.error(f"Failed to initialize TelegramGateway: {e}")
            return False

    async def shutdown(self) -> None:
        """Завершает работу шлюза."""
        try:
            self._initialized = False
            self._logger.info("TelegramGateway shut down successfully")
        except Exception as e:
            self._logger.error(f"Error shutting down TelegramGateway: {e}")

    async def health_check(self) -> bool:
        """Проверяет состояние шлюза."""
        return self._initialized

    async def recover(self) -> bool:
        """Восстанавливает работу шлюза после сбоя."""
        try:
            if not self._initialized:
                return await self.initialize()
            return True
        except Exception as e:
            self._logger.error(f"Failed to recover TelegramGateway: {e}")
            return False

    def _create_keyboard_markup(
        self, buttons: List[List[Button]]
    ) -> Optional[InlineKeyboardMarkup]:
        """Создает разметку клавиатуры для Telegram"""
        if not buttons:
            return None

        keyboard = []
        for row in buttons:
            keyboard_row = []
            for button in row:
                keyboard_row.append(
                    InlineKeyboardButton(
                        text=button.text,
                        callback_data=button.callback_data,
                    )
                )
            keyboard.append(keyboard_row)
        return InlineKeyboardMarkup(keyboard)

    async def send(self, message: OutboundMessage) -> None:
        """Отправляет сообщение через Telegram"""
        try:
            keyboard = None
            if message.keyboard_buttons:
                keyboard = self._create_keyboard_markup(message.keyboard_buttons)

            await self._client.send_message(
                chat_id=message.recipient_id,
                message=Message(
                    text=message.content,
                    keyboard_buttons=message.keyboard_buttons,
                    parse_mode=message.format,
                ),
            )
            self._logger.debug(
                f"Message sent successfully to {message.recipient_id}: {message.content[:50]}..."
            )
        except Exception as e:
            self._logger.error(f"Failed to send message: {e}")
            raise

    async def edit(self, message_id: str, message: OutboundMessage) -> None:
        """Редактирует существующее сообщение в Telegram"""
        try:
            keyboard = None
            if message.keyboard_buttons:
                keyboard = self._create_keyboard_markup(message.keyboard_buttons)

            await self._client.edit_message(
                chat_id=message.recipient_id,
                message_id=message_id,
                message=Message(
                    text=message.content,
                    keyboard_buttons=message.keyboard_buttons,
                    parse_mode=message.format,
                ),
            )
            self._logger.debug(
                f"Message {message_id} edited successfully in {message.recipient_id}: {message.content[:50]}..."
            )
        except Exception as e:
            self._logger.error(f"Failed to edit message: {e}")
            raise

    async def delete(self, recipient_id: str, message_id: str) -> bool:
        """Удаляет сообщение в Telegram"""
        try:
            return await self._client.delete_message(
                chat_id=recipient_id,
                message_id=message_id,
            )
        except Exception as e:
            self._logger.error(f"Failed to delete message: {e}")
            return False

    async def answer_callback(
        self, callback_id: str, text: Optional[str] = None
    ) -> None:
        """Отвечает на callback query в Telegram"""
        try:
            await self._client.answer_callback(
                callback_id=callback_id,
                text=text,
            )
            if text:
                self._logger.debug(
                    f"Callback query {callback_id} answered with text: {text}"
                )
            else:
                self._logger.debug(
                    f"Callback query {callback_id} answered without text"
                )
        except Exception as e:
            self._logger.error(f"Failed to answer callback: {e}")
            raise
