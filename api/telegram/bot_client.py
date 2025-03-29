# Created by setup script

from typing import Optional, Dict, Any, Callable
from functools import wraps
import logging
import traceback
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from dark_archive.application.interfaces.telegram_client import ITelegramClient
from dark_archive.application.interfaces.message_gateway import IMessageGateway
from dark_archive.domain.value_objects.message import OutboundMessage, Button
from dark_archive.domain.lifecycle.base_lifecycle_manager import BaseLifecycleManager
import asyncio

logger = logging.getLogger(__name__)


def log_async_errors(func):
    """Декоратор для логирования ошибок в асинхронных функциях"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Error in {func.__name__}: {e}\n"
                f"Args: {args}\n"
                f"Kwargs: {kwargs}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise

    return wrapper


async def stop_with_timeout(coro, timeout=5.0):
    """Выполняет корутину с таймаутом"""
    try:
        return await asyncio.wait_for(coro, timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout}s")


class TelegramClientAdapter(BaseLifecycleManager, ITelegramClient, IMessageGateway):
    """Adapter for Telegram bot client with lifecycle management."""

    def __init__(self, token: str):
        super().__init__()
        self._token = token
        self._application: Optional[Application] = None
        self._bot: Optional[Bot] = None
        self._message_handler: Optional[
            Callable[[Update, ContextTypes.DEFAULT_TYPE], Any]
        ] = None
        self._message_lock = asyncio.Lock()
        self._callback_lock = asyncio.Lock()
        logger.info("TelegramClientAdapter initialized")

    def set_message_handler(
        self, handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Any]
    ) -> None:
        """Set the message handler for the bot."""
        self._message_handler = handler
        if self._application and self.is_healthy():
            self._setup_handlers()

    async def send_message(self, chat_id: int, message: OutboundMessage) -> None:
        """Отправляет сообщение"""
        async with self._message_lock:
            if not self._initialized or self._app is None:
                try:
                    logger.warning("Client not initialized, attempting to reinitialize")
                    await self.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize client on-demand: {e}")
                    raise RuntimeError("Client not initialized")

            try:
                # Создаем клавиатуру, если есть кнопки
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

                await self._app.bot.send_message(
                    chat_id=chat_id,
                    text=message.content,
                    parse_mode=message.format,
                    reply_markup=reply_markup,
                )
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                raise

    def _do_initialize(self) -> bool:
        """Initialize the Telegram bot."""
        try:
            self._application = Application.builder().token(self._token).build()
            self._bot = self._application.bot
            if self._message_handler:
                self._setup_handlers()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            self._last_error = e
            return False

    def _do_shutdown(self) -> None:
        """Shutdown the Telegram bot."""
        if self._application:
            try:
                self._application.stop()
                self._application.shutdown()
            except Exception as e:
                logger.error(f"Error during Telegram bot shutdown: {e}")
                raise
        self._application = None
        self._bot = None

    def _check_health(self) -> bool:
        """Check if the bot is healthy."""
        try:
            return bool(self._application and self._bot and self._application.running)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._last_error = e
            return False

    def _do_recover(self) -> bool:
        """Attempt to recover the bot."""
        try:
            self.shutdown()
            return self.initialize()
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            self._last_error = e
            return False

    def _setup_handlers(self) -> None:
        """Setup message handlers for the bot."""
        if not self._application or not self._message_handler:
            return

        # Add handlers
        self._application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._message_handler)
        )

        # Add basic command handlers
        self._application.add_handler(CommandHandler("start", self._start_command))
        self._application.add_handler(CommandHandler("help", self._help_command))

    async def _start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command."""
        await update.message.reply_text(
            "Добро пожаловать в Dark Archive! Я помогу вам расследовать паранормальные явления."
        )

    async def _help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        help_text = """
        Доступные команды:
        /start - Начать работу с ботом
        /help - Показать это сообщение
        
        Для начала расследования просто отправьте мне сообщение с описанием ситуации.
        """
        await update.message.reply_text(help_text)

    async def start(self) -> None:
        """Start the bot."""
        if not self.initialize():
            raise RuntimeError("Failed to initialize Telegram bot")
        await self._application.start()

    async def stop(self) -> None:
        """Stop the bot."""
        self.shutdown()

    async def initialize(self) -> None:
        """Инициализация клиента"""
        if self._initialized:
            logger.info("Client already initialized")
            return

        try:
            logger.info("Initializing Telegram client...")
            self._app = Application.builder().token(self._token).build()
            await self._app.initialize()
            self._initialized = True
            logger.info("Telegram client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            self._initialized = False
            raise

    async def add_handler(self, handler: Callable) -> None:
        """Добавляет обработчик команды"""
        if not self._initialized:
            await self.initialize()

        try:
            # Получаем имя метода и убираем суффикс '_command'
            handler_name = handler.__name__
            if handler_name.endswith("_command"):
                command = handler_name[:-8]  # Убираем '_command'
                command_handler = CommandHandler(command, handler)
                self._app.add_handler(command_handler)
                logger.info(f"Added command handler for /{command}")
            elif handler_name == "button_handler":
                self.add_callback_query_handler(handler)
            else:
                logger.warning(f"Unknown handler type: {handler_name}")
        except Exception as e:
            logger.error(f"Failed to add handler: {e}")
            raise

    def add_callback_query_handler(self, handler: Callable) -> None:
        """Добавляет обработчик callback query"""
        if not self._initialized:
            raise RuntimeError("Client not initialized")

        try:
            callback_handler = CallbackQueryHandler(handler)
            self._app.add_handler(callback_handler)
            logger.info(f"Added callback query handler: {handler.__name__}")
        except Exception as e:
            logger.error(f"Failed to add callback query handler: {e}")
            raise

    async def start(self) -> None:
        """Запускает бота"""
        if not self._initialized:
            await self.initialize()

        try:
            logger.info("Starting bot...")
            await self._app.start()
            await self._app.updater.start_polling()
            logger.info("Bot started successfully")
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

    async def stop(self) -> None:
        """Останавливает бота"""
        if not self._app:
            return

        try:
            logger.info("Stopping bot...")
            await self._app.stop()
            self._initialized = False
            logger.info("Bot stopped successfully")
        except Exception as e:
            logger.error(f"Failed to stop bot: {e}")
            raise

    async def edit_message(
        self, chat_id: int, message_id: int, message: OutboundMessage
    ) -> None:
        """Редактирует сообщение"""
        async with self._message_lock:
            if not self._initialized or self._app is None:
                try:
                    logger.warning("Client not initialized, attempting to reinitialize")
                    await self.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize client on-demand: {e}")
                    raise RuntimeError("Client not initialized")

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

                await self._app.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=message.content,
                    parse_mode=message.format,
                    reply_markup=reply_markup,
                )
            except Exception as e:
                logger.error(f"Failed to edit message: {e}")
                raise

    async def answer_callback(
        self, callback_id: str, text: Optional[str] = None
    ) -> None:
        """Отвечает на callback query"""
        async with self._callback_lock:
            if not self._initialized or self._app is None:
                try:
                    logger.warning("Client not initialized, attempting to reinitialize")
                    await self.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize client on-demand: {e}")
                    raise RuntimeError("Client not initialized")

            try:
                await self._app.bot.answer_callback_query(
                    callback_query_id=callback_id,
                    text=text,
                )
            except Exception as e:
                logger.error(f"Failed to answer callback: {e}")
                raise

    @log_async_errors
    async def delete_message(self, chat_id: str, message_id: str) -> bool:
        """Удаляет сообщение

        Args:
            chat_id: ID чата
            message_id: ID сообщения

        Returns:
            bool: True если сообщение успешно удалено
        """
        if not self._app:
            raise RuntimeError("Client not initialized")

        try:
            await self._app.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
            logger.debug(
                f"Message {message_id} deleted successfully from chat {chat_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete message: {e}\n{traceback.format_exc()}")
            return False
