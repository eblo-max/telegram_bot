from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect


class AIService(ABC):
    """Базовый интерфейс для работы с AI сервисами"""

    @abstractmethod
    async def generate_case(self, difficulty: int = 5) -> Optional[Dict]:
        """Генерирует новое расследование

        Args:
            difficulty: Сложность расследования (1-10)

        Returns:
            Optional[Dict]: Словарь с данными расследования или None в случае ошибки
        """
        pass

    @abstractmethod
    async def analyze_evidence(
        self, case: Case, evidence: Evidence, context: Optional[Dict[str, str]] = None
    ) -> str:
        """Анализирует улику и предоставляет выводы

        Args:
            case: Текущее дело
            evidence: Улика для анализа
            context: Дополнительный контекст

        Returns:
            str: Результаты анализа
        """
        pass

    @abstractmethod
    async def generate_location_description(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует описание локации с учетом найденных улик

        Args:
            case: Текущее дело
            location: Локация для описания
            discovered_evidence: Найденные улики в локации

        Returns:
            str: Описание локации
        """
        pass

    @abstractmethod
    async def evaluate_theory(
        self, case: Case, theory: str, evidence_ids: List[UUID]
    ) -> Dict[str, float]:
        """Оценивает теорию игрока

        Args:
            case: Текущее дело
            theory: Теория игрока
            evidence_ids: Список ID улик, использованных в теории

        Returns:
            Dict[str, float]: Оценка теории (точность, полнота, связность)
        """
        pass

    @abstractmethod
    async def generate_hint(
        self, case: Case, current_progress: float, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует подсказку для игрока

        Args:
            case: Текущее дело
            current_progress: Текущий прогресс расследования (0-1)
            discovered_evidence: Список найденных улик

        Returns:
            str: Подсказка для игрока
        """
        pass

    @abstractmethod
    async def analyze_suspect(
        self, case: Case, suspect: Suspect, evidence: List[Evidence]
    ) -> Dict[str, str]:
        """Анализирует подозреваемого

        Args:
            case: Текущее дело
            suspect: Подозреваемый для анализа
            evidence: Список улик, связанных с подозреваемым

        Returns:
            Dict[str, str]: Результаты анализа
        """
        pass

    @abstractmethod
    async def generate_interrogation(
        self, case: Case, suspect: Suspect, evidence: List[Evidence]
    ) -> List[Dict[str, str]]:
        """Генерирует диалог допроса

        Args:
            case: Текущее дело
            suspect: Подозреваемый для допроса
            evidence: Список улик для использования в допросе

        Returns:
            List[Dict[str, str]]: Список реплик допроса
        """
        pass


class IAIService(ABC):
    """Интерфейс для сервиса искусственного интеллекта."""

    @abstractmethod
    async def analyze_text(
        self, text: str, instruction: str, context: Optional[Dict[str, str]] = None
    ) -> Optional[Dict]:
        """Анализирует текст с помощью AI."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        context: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Генерирует текст с помощью AI."""
        pass

    @abstractmethod
    async def get_embedding(self, text: str) -> Optional[list[float]]:
        """Получает эмбеддинги для текста."""
        pass
