from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class State(Enum):
    """Базовые состояния бота"""

    IDLE = "idle"  # Ожидание команды
    CREATING_CASE = "creating_case"  # Создание нового дела
    INVESTIGATING = "investigating"  # Расследование
    ANALYZING = "analyzing"  # Анализ улик
    INTERROGATING = "interrogating"  # Допрос
    THEORIZING = "theorizing"  # Построение теории


@dataclass
class StateContext:
    """Контекст состояния"""

    user_id: int
    chat_id: int
    state: State
    data: Optional[Dict[str, Any]] = None


class StateHandler(ABC):
    """Базовый интерфейс для обработчиков состояний"""

    @abstractmethod
    async def handle(self, context: StateContext) -> None:
        """Обрабатывает состояние

        Args:
            context: Контекст состояния
        """
        pass

    @abstractmethod
    async def can_handle(self, state: State) -> bool:
        """Проверяет, может ли обработчик обработать состояние

        Args:
            state: Состояние для проверки

        Returns:
            bool: True если обработчик может обработать состояние
        """
        pass


class StateManager:
    """Менеджер состояний"""

    def __init__(self):
        self._handlers: Dict[State, StateHandler] = {}
        self._user_states: Dict[int, StateContext] = {}

    def register_handler(self, state: State, handler: StateHandler) -> None:
        """Регистрирует обработчик для состояния

        Args:
            state: Состояние
            handler: Обработчик состояния
        """
        self._handlers[state] = handler

    async def set_state(
        self,
        user_id: int,
        chat_id: int,
        state: State,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Устанавливает состояние для пользователя

        Args:
            user_id: ID пользователя
            chat_id: ID чата
            state: Новое состояние
            data: Дополнительные данные состояния
        """
        context = StateContext(user_id=user_id, chat_id=chat_id, state=state, data=data)
        self._user_states[user_id] = context

        handler = self._handlers.get(state)
        if handler and await handler.can_handle(state):
            await handler.handle(context)

    def get_state(self, user_id: int) -> Optional[StateContext]:
        """Получает текущее состояние пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Optional[StateContext]: Контекст текущего состояния или None
        """
        return self._user_states.get(user_id)

    def clear_state(self, user_id: int) -> None:
        """Очищает состояние пользователя

        Args:
            user_id: ID пользователя
        """
        if user_id in self._user_states:
            del self._user_states[user_id]


class BaseStateHandler(StateHandler):
    """Базовый класс для обработчиков состояний"""

    def __init__(self, states: list[State]):
        self._states = states

    async def can_handle(self, state: State) -> bool:
        """Проверяет, может ли обработчик обработать состояние"""
        return state in self._states
