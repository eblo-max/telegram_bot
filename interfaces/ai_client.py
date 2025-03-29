from abc import ABC, abstractmethod
from typing import List, Dict, Any

from dark_archive.domain.interfaces.lifecycle_manager import ILifecycleManager


class IAIClient(ILifecycleManager, ABC):
    """Интерфейс для AI клиента."""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """Генерирует ответ от AI."""
        pass
