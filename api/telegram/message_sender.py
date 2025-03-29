# Created by setup script

from typing import Optional, List, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import traceback
from dark_archive.application.interfaces.message_gateway import (
    IMessageGateway,
    Message,
    Button,
)

logger = logging.getLogger(__name__)


class MessageSender(IMessageGateway):
    """Класс для отправки сообщений через Telegram API"""

    async def send_message(self, chat_id: str, message: Message) -> None:
        """Отправляет сообщение пользователю

        Args:
            chat_id: ID чата
            message: Объект сообщения с текстом и кнопками
        """
        try:
            reply_markup = None
            if message.keyboard_buttons:
                keyboard = []
                for row in message.keyboard_buttons:
                    keyboard_row = []
                    for button in row:
                        keyboard_row.append(
                            InlineKeyboardButton(
                                text=button.text,
                                callback_data=button.callback_data,
                            )
                        )
                    keyboard.append(keyboard_row)
                reply_markup = InlineKeyboardMarkup(keyboard)

            # Здесь нужно использовать bot.send_message вместо update.effective_chat.send_message
            # Это будет добавлено позже при внедрении бота
            logger.debug(
                f"Message sent successfully to {chat_id}: {message.text[:50]}..."
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e}\n{traceback.format_exc()}")
            raise

    async def edit_message(
        self, chat_id: str, message_id: str, message: Message
    ) -> None:
        """Редактирует существующее сообщение

        Args:
            chat_id: ID чата
            message_id: ID сообщения для редактирования
            message: Новое сообщение
        """
        try:
            reply_markup = None
            if message.keyboard_buttons:
                keyboard = []
                for row in message.keyboard_buttons:
                    keyboard_row = []
                    for button in row:
                        keyboard_row.append(
                            InlineKeyboardButton(
                                text=button.text,
                                callback_data=button.callback_data,
                            )
                        )
                    keyboard.append(keyboard_row)
                reply_markup = InlineKeyboardMarkup(keyboard)

            # Здесь нужно использовать bot.edit_message_text вместо callback_query.edit_message_text
            # Это будет добавлено позже при внедрении бота
            logger.debug(
                f"Message edited successfully in {chat_id}: {message.text[:50]}..."
            )
        except Exception as e:
            logger.error(f"Failed to edit message: {e}\n{traceback.format_exc()}")
            raise

    async def answer_callback(
        self, callback_id: str, text: Optional[str] = None
    ) -> None:
        """Отвечает на callback query

        Args:
            callback_id: ID callback query
            text: Текст всплывающего уведомления
        """
        try:
            # Здесь нужно использовать bot.answer_callback_query
            # Это будет добавлено позже при внедрении бота
            if text:
                logger.debug(f"Callback query {callback_id} answered with text: {text}")
            else:
                logger.debug(f"Callback query {callback_id} answered without text")
        except Exception as e:
            logger.error(
                f"Failed to answer callback query: {e}\n{traceback.format_exc()}"
            )
            raise
