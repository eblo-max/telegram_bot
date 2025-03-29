import asyncio
import logging
import os
import signal
import sys
from pathlib import Path
from contextlib import asynccontextmanager, suppress
from typing import AsyncIterator, NoReturn, Set

from dotenv import load_dotenv
from dependency_injector.wiring import inject, Provide

from dark_archive.infrastructure.container import Container
from dark_archive.utils.dependency_checker import check_dependencies
from dark_archive.di.container import create_container
from dark_archive.config.settings import settings
from dark_archive.domain.services.case_service import CaseService
from dark_archive.infrastructure.repositories.redis_case_repository import (
    RedisCaseRepository,
)

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Устанавливаем уровень DEBUG для более детального логирования
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Настраиваем логирование для dependency_injector
di_logger = logging.getLogger("dependency_injector")
di_logger.setLevel(logging.DEBUG)


def setup_asyncio_windows() -> None:
    """Настройка asyncio для Windows"""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan() -> AsyncIterator[None]:
    """Контекстный менеджер для управления жизненным циклом приложения"""
    # Создаем объект события для graceful shutdown
    stop_event = asyncio.Event()

    # Определяем обработчик сигналов
    def signal_handler():
        logger.info("Received stop signal")
        stop_event.set()

    # Регистрируем обработчики сигналов
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        yield
    finally:
        # Удаляем обработчики сигналов
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.remove_signal_handler(sig)


@inject
async def run_bot(
    container: Container = Provide[Container],
) -> NoReturn:
    """Запускает бота и управляет его жизненным циклом"""
    logger.info("Starting the bot")
    telegram_client = container.telegram_client()
    handlers = container.telegram_handlers()

    # Инициализируем клиент
    logger.debug("Initializing Telegram client")
    await telegram_client.initialize()

    # Регистрируем обработчики
    logger.debug("Registering message handlers")
    for handler in handlers.get_handlers():
        await telegram_client.add_handler(handler)

    # Запускаем бота
    logger.info("Starting Telegram client")
    await telegram_client.start()

    try:
        # Бесконечный цикл для поддержания работы бота
        logger.info("Bot is running")
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        # Graceful shutdown при отмене задачи
        logger.info("Shutting down...")
        await telegram_client.stop()


class Application:
    """Main application class."""

    def __init__(self):
        self.container = create_container()
        self.container.config.from_dict(
            {
                "telegram": {"token": settings.TELEGRAM_TOKEN},
                "redis": {
                    "url": settings.REDIS_URL,
                    "enabled": settings.REDIS_ENABLED,
                    "case_prefix": settings.REDIS_CASE_PREFIX,
                },
                "storage": {"cases_path": settings.CASES_STORAGE_PATH},
                "ai": {"provider": settings.AI_PROVIDER},
                "claude": {"api_key": settings.ANTHROPIC_API_KEY},
                "openai": {"api_key": settings.OPENAI_API_KEY},
                "cache": {"prefix": settings.CACHE_PREFIX},
            }
        )
        self._shutdown_event = asyncio.Event()
        self._tasks: Set[asyncio.Task] = set()

    async def start(self):
        """Start the application."""
        try:
            # Initialize components
            monitor = self.container.lifecycle_monitor()
            if not monitor.initialize_all():
                raise RuntimeError("Failed to initialize components")

            # Start lifecycle monitoring
            await monitor.start_monitoring()
            self._tasks.add(asyncio.create_task(self._monitor_health()))

            # Start Telegram bot
            telegram_client = self.container.telegram_client()
            await telegram_client.start()

            # Setup signal handlers
            for sig in (signal.SIGTERM, signal.SIGINT):
                asyncio.get_event_loop().add_signal_handler(
                    sig, lambda s=sig: asyncio.create_task(self.shutdown(s))
                )

            logger.info("Application started successfully")
            await self._shutdown_event.wait()

        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            raise

    async def shutdown(self, sig=None):
        """Shutdown the application."""
        if sig:
            logger.info(f"Received shutdown signal: {sig.name}")

        try:
            # Stop lifecycle monitoring
            monitor = self.container.lifecycle_monitor()
            await monitor.shutdown()

            # Cancel all tasks
            for task in self._tasks:
                task.cancel()
            await asyncio.gather(*self._tasks, return_exceptions=True)

            self._shutdown_event.set()
            logger.info("Application shutdown complete")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            raise

    async def _monitor_health(self):
        """Monitor application health."""
        monitor = self.container.lifecycle_monitor()
        while True:
            try:
                statuses = monitor.get_all_statuses()
                unhealthy = [s for s in statuses if not s["healthy"]]
                if unhealthy:
                    logger.warning(f"Unhealthy components: {unhealthy}")
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)


@asynccontextmanager
async def run_app():
    """Run the application with proper startup and shutdown."""
    app = Application()
    try:
        await app.start()
        yield app
    finally:
        await app.shutdown()


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    async def run():
        async with run_app() as app:
            await app._shutdown_event.wait()

    asyncio.run(run())


if __name__ == "__main__":
    setup_asyncio_windows()
    # Запускаем приложение
    main()
