from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from dataclasses import dataclass

TCommand = TypeVar("TCommand")
TResult = TypeVar("TResult")


class BaseUseCase(ABC, Generic[TCommand, TResult]):
    """Базовый класс для всех use case."""

    @abstractmethod
    async def execute(self, command: TCommand) -> TResult:
        """Асинхронное выполнение use case."""
        pass

    def execute_sync(self, command: TCommand) -> TResult:
        """Синхронное выполнение use case."""
        import asyncio

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.execute(command))
