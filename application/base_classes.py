from abc import ABC
from uuid import UUID, uuid4
from datetime import datetime


class BaseEntity(ABC):
    """Базовый класс для всех сущностей."""

    def __init__(self, id: UUID | str | None = None):
        """
        Инициализирует сущность.

        Args:
            id: Идентификатор сущности. Если не указан, генерируется новый.
        """
        self._id = uuid4() if id is None else (UUID(id) if isinstance(id, str) else id)
        self._created_at: datetime = datetime.utcnow()
        self._updated_at: datetime = self._created_at

    @property
    def id(self) -> UUID:
        """Получить ID сущности."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Получить время создания сущности."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Получить время последнего обновления сущности."""
        return self._updated_at

    def _update_timestamp(self):
        """Обновить временную метку последнего изменения."""
        self._updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        """
        Сравнивает две сущности.

        Args:
            other: Другая сущность

        Returns:
            bool: True если сущности равны, False в противном случае
        """
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Возвращает хеш сущности.

        Returns:
            int: Хеш сущности
        """
        return hash(self.id)
