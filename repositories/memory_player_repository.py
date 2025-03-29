from typing import Dict, Optional, List
from uuid import UUID
from dataclasses import dataclass, field

from dark_archive.application.interfaces.repository import Repository
from dark_archive.domain.entities.player import Player


@dataclass
class MemoryPlayerRepository(Repository[Player]):
    """Репозиторий игроков в памяти для тестирования."""

    _players: Dict[UUID, Player] = field(default_factory=dict)
    _players_by_telegram_id: Dict[int, Player] = field(default_factory=dict)
    _initialized: bool = False

    async def initialize(self) -> bool:
        """Инициализирует репозиторий."""
        self._initialized = True
        return True

    async def shutdown(self) -> bool:
        """Завершает работу репозитория."""
        self._initialized = False
        return True

    def is_healthy(self) -> bool:
        """Проверяет здоровье репозитория."""
        return self._initialized

    async def get(self, id: UUID) -> Optional[Player]:
        """Получает игрока по идентификатору."""
        return self._players.get(id)

    async def get_all(self) -> List[Player]:
        """Получает всех игроков."""
        return list(self._players.values())

    async def save(self, player: Player) -> Player:
        """Сохраняет игрока."""
        self._players[player.id] = player
        self._players_by_telegram_id[player.telegram_id] = player
        return player

    async def update(self, player: Player) -> Player:
        """Обновляет игрока."""
        if player.id not in self._players:
            raise ValueError(f"Player with id {player.id} not found")
        self._players[player.id] = player
        self._players_by_telegram_id[player.telegram_id] = player
        return player

    async def delete(self, id: UUID) -> None:
        """Удаляет игрока."""
        if id in self._players:
            player = self._players[id]
            del self._players_by_telegram_id[player.telegram_id]
            del self._players[id]

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Player]:
        """Получает игрока по Telegram ID."""
        return self._players_by_telegram_id.get(telegram_id)

    async def delete_by_telegram_id(self, telegram_id: int) -> None:
        """Удаляет игрока по Telegram ID."""
        if telegram_id in self._players_by_telegram_id:
            player = self._players_by_telegram_id[telegram_id]
            del self._players[player.id]
            del self._players_by_telegram_id[telegram_id]
