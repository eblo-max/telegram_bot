from abc import ABC, abstractmethod
from typing import TypeVar, Generic


class BaseQuery(ABC):
    """Базовый класс для запросов."""

    pass


TQuery = TypeVar("TQuery", bound=BaseQuery)
TResult = TypeVar("TResult")


class QueryHandler(Generic[TQuery, TResult], ABC):
    """Базовый интерфейс для обработчиков запросов."""

    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        """Обрабатывает запрос."""
        pass
