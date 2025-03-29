from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar

T = TypeVar("T")


class ISerializer(ABC):
    """Интерфейс для сериализации/десериализации объектов"""

    @abstractmethod
    def serialize(self, obj: Any) -> Dict:
        """
        Сериализует объект в словарь.

        Args:
            obj: Объект для сериализации

        Returns:
            Dict: Сериализованный объект
        """
        pass

    @abstractmethod
    def deserialize(self, data: Dict, cls: type[T]) -> T:
        """
        Десериализует словарь в объект указанного типа.

        Args:
            data: Словарь с данными
            cls: Тип объекта для десериализации

        Returns:
            T: Десериализованный объект
        """
        pass

    @abstractmethod
    def save_to_file(self, obj: Any, filepath: str) -> None:
        """
        Сохраняет объект в файл.

        Args:
            obj: Объект для сохранения
            filepath: Путь к файлу
        """
        pass

    @abstractmethod
    def load_from_file(self, filepath: str, cls: type[T]) -> Optional[T]:
        """
        Загружает объект из файла.

        Args:
            filepath: Путь к файлу
            cls: Тип объекта для загрузки

        Returns:
            Optional[T]: Загруженный объект или None в случае ошибки
        """
        pass
