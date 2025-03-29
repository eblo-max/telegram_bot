from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass
class TCommand:
    """Базовый класс для команд."""

    pass


TResult = TypeVar("TResult")
TCommandType = TypeVar("TCommandType", bound=TCommand)


class CommandHandler(Generic[TCommandType, TResult], ABC):
    """Базовый класс для обработчиков команд."""

    @abstractmethod
    async def handle(self, command: TCommandType) -> TResult:
        """Обрабатывает команду."""
        pass
