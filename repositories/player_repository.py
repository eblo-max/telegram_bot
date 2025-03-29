# Created by setup script

from abc import ABC, abstractmethod
from typing import Optional, List

from dark_archive.domain.entities.player import Player


class PlayerRepository(ABC):
    """Интерфейс репозитория для работы с игроками."""

    @abstractmethod
    async def get_by_id(self, player_id: str) -> Optional[Player]:
        """Получить игрока по id."""
        pass

    @abstractmethod
    async def save(self, player: Player) -> None:
        """Сохранить игрока."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[Player]:
        """Получить игрока по имени пользователя."""
        pass

    @abstractmethod
    async def get_all_active(self) -> List[Player]:
        """Получить всех активных игроков."""
        pass
