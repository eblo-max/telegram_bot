import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar

from dark_archive.domain.interfaces.serialization import ISerializer

logger = logging.getLogger(__name__)
T = TypeVar("T")


class JsonSerializer(ISerializer):
    """Реализация сериализатора для работы с JSON"""

    def serialize(self, obj: Any) -> Dict:
        """Сериализует объект в словарь"""
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        raise ValueError(f"Object {obj} cannot be serialized to JSON")

    def deserialize(self, data: Dict, cls: type[T]) -> T:
        """Десериализует словарь в объект указанного типа"""
        try:
            return cls(**data)
        except Exception as e:
            logger.error(f"Failed to deserialize {data} to {cls}: {str(e)}")
            raise

    def save_to_file(self, obj: Any, filepath: str) -> None:
        """Сохраняет объект в JSON файл"""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.serialize(obj), f, indent=2, ensure_ascii=False)

            logger.debug(f"Object saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save object to {filepath}: {str(e)}")
            raise

    def load_from_file(self, filepath: str, cls: type[T]) -> Optional[T]:
        """Загружает объект из JSON файла"""
        try:
            if not Path(filepath).exists():
                return None

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            return self.deserialize(data, cls)
        except Exception as e:
            logger.error(f"Failed to load object from {filepath}: {str(e)}")
            return None
