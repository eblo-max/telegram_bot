import asyncio
import functools
import logging
from typing import TypeVar, Callable, Any

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceInitializationError(Exception):
    """Ошибка инициализации сервиса."""

    pass


def handle_init_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Декоратор для обработки ошибок инициализации сервисов."""

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Service initialization failed: {e}", exc_info=True)
            raise ServiceInitializationError(f"Failed to initialize service: {str(e)}")

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Service initialization failed: {e}", exc_info=True)
            raise ServiceInitializationError(f"Failed to initialize service: {str(e)}")

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
