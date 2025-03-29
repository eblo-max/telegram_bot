from abc import ABC, abstractmethod
from typing import Dict, Optional
from dark_archive.domain.interfaces.lifecycle_manager import ILifecycleManager


class ILLMClient(ILifecycleManager, ABC):
    """Интерфейс для взаимодействия с языковыми моделями"""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """
        Генерирует текст на основе промпта.

        Args:
            prompt: Текст промпта
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура генерации (0.0 - 1.0)
            context: Дополнительный контекст для генерации

        Returns:
            Optional[str]: Сгенерированный текст или None в случае ошибки
        """
        pass

    @abstractmethod
    async def analyze_text(
        self, text: str, instruction: str, context: Optional[Dict[str, str]] = None
    ) -> Optional[Dict]:
        """
        Анализирует текст согласно инструкции.

        Args:
            text: Текст для анализа
            instruction: Инструкция по анализу
            context: Дополнительный контекст

        Returns:
            Optional[Dict]: Результат анализа или None в случае ошибки
        """
        pass

    @abstractmethod
    async def get_embedding(self, text: str) -> Optional[list[float]]:
        """
        Получает векторное представление текста.

        Args:
            text: Текст для векторизации

        Returns:
            Optional[list[float]]: Вектор или None в случае ошибки
        """
        pass
