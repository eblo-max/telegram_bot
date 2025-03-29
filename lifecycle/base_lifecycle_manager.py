from typing import Optional
import logging
from enum import Enum
from threading import Lock
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager

from dark_archive.domain.interfaces.lifecycle_manager import ILifecycleManager

logger = logging.getLogger(__name__)


class ComponentStatus(Enum):
    """Enumeration of possible component statuses."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    RECOVERING = "recovering"


class BaseLifecycleManager(ILifecycleManager, ABC):
    """Базовый класс для управления жизненным циклом компонентов."""

    def __init__(self):
        self._status = ComponentStatus.UNINITIALIZED
        self._last_error: Optional[Exception] = None
        self._lock = Lock()
        self._initialized = False

    def initialize(self) -> bool:
        """Инициализирует компонент."""
        if self._initialized:
            return True

        try:
            logger.info(f"Initializing {self.__class__.__name__}")
            self._status = ComponentStatus.INITIALIZING
            if self._do_initialize():
                self._initialized = True
                self._last_error = None
                self._status = ComponentStatus.RUNNING
                logger.info(f"{self.__class__.__name__} initialized successfully")
                return True
            else:
                self._status = ComponentStatus.ERROR
                logger.error(f"Failed to initialize {self.__class__.__name__}")
                return False
        except Exception as e:
            self._last_error = e
            self._status = ComponentStatus.ERROR
            logger.error(
                f"Error initializing {self.__class__.__name__}: {e}", exc_info=True
            )
            return False

    def shutdown(self) -> None:
        """Останавливает компонент."""
        if not self._initialized:
            return

        try:
            logger.info(f"Shutting down {self.__class__.__name__}")
            self._status = ComponentStatus.STOPPING
            self._do_shutdown()
            self._initialized = False
            self._status = ComponentStatus.STOPPED
            logger.info(f"{self.__class__.__name__} shut down successfully")
        except Exception as e:
            self._last_error = e
            self._status = ComponentStatus.ERROR
            logger.error(
                f"Error shutting down {self.__class__.__name__}: {e}", exc_info=True
            )
            raise

    def is_healthy(self) -> bool:
        """Проверяет здоровье компонента."""
        if not self._initialized:
            return False
        try:
            return self._check_health()
        except Exception as e:
            self._last_error = e
            self._status = ComponentStatus.ERROR
            logger.error(f"{self.__class__.__name__} health check failed: {e}")
            return False

    def recover(self) -> bool:
        """Пытается восстановить компонент."""
        try:
            logger.info(f"Attempting to recover {self.__class__.__name__}")
            self._status = ComponentStatus.RECOVERING
            if self._do_recover():
                self._last_error = None
                self._status = ComponentStatus.RUNNING
                logger.info(f"{self.__class__.__name__} recovered successfully")
                return True
            else:
                self._status = ComponentStatus.ERROR
                logger.error(f"Failed to recover {self.__class__.__name__}")
                return False
        except Exception as e:
            self._last_error = e
            self._status = ComponentStatus.ERROR
            logger.error(
                f"Error recovering {self.__class__.__name__}: {e}", exc_info=True
            )
            return False

    @property
    def status(self) -> str:
        """Возвращает текущий статус компонента."""
        if not self._initialized:
            return "stopped"
        if self._status == ComponentStatus.ERROR:
            return "unhealthy"
        if self.is_healthy():
            return "healthy"
        return "unhealthy"

    @property
    def last_error(self) -> Optional[Exception]:
        """Возвращает последнюю ошибку."""
        return self._last_error

    @abstractmethod
    def _do_initialize(self) -> bool:
        """Выполняет инициализацию компонента."""
        pass

    @abstractmethod
    def _do_shutdown(self) -> None:
        """Выполняет остановку компонента."""
        pass

    @abstractmethod
    def _check_health(self) -> bool:
        """Проверяет здоровье компонента."""
        pass

    @abstractmethod
    def _do_recover(self) -> bool:
        """Выполняет восстановление компонента."""
        pass

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        if not self.initialize():
            raise RuntimeError(f"Failed to initialize {self.__class__.__name__}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        self.shutdown()

    @asynccontextmanager
    async def managed(self):
        """Контекстный менеджер для автоматического управления жизненным циклом."""
        try:
            if not self.initialize():
                raise RuntimeError(f"Failed to initialize {self.__class__.__name__}")
            yield self
        finally:
            self.shutdown()
