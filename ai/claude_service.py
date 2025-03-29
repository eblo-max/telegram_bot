import logging
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime
import anthropic

from dark_archive.application.interfaces.ai_service import IAIService
from dark_archive.domain.models.case import (
    Case,
    Evidence,
    Location,
    CaseStatus,
    EvidenceType,
)
from dark_archive.domain.interfaces.ai_service import AIService
from dark_archive.domain.entities.suspect import Suspect

logger = logging.getLogger(__name__)


class ClaudeService(IAIService):
    """Реализация AI сервиса с использованием Claude API"""

    def __init__(self, api_key: str):
        """Инициализация сервиса

        Args:
            api_key: Ключ API для доступа к Claude
        """
        self.client = anthropic.Client(api_key=api_key)
        logger.info("ClaudeService initialized")

    async def generate_investigation(
        self,
        difficulty: int,
        theme: Optional[str] = None,
        constraints: Optional[Dict[str, str]] = None,
    ) -> Case:
        """Генерирует новое расследование"""
        try:
            # Формируем промпт для генерации
            prompt = self._build_investigation_prompt(difficulty, theme, constraints)

            # Получаем ответ от Claude
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4096,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )

            # Парсим ответ и создаем объект Case
            case_data = self._parse_investigation_response(response.content)

            return case_data

        except Exception as e:
            logger.error(f"Error generating investigation: {e}")
            raise

    async def analyze_evidence(
        self, case: Case, evidence: Evidence, context: Optional[Dict[str, str]] = None
    ) -> str:
        """Анализирует улику"""
        try:
            prompt = self._build_evidence_analysis_prompt(case, evidence, context)

            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2048,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content

        except Exception as e:
            logger.error(f"Error analyzing evidence: {e}")
            raise

    async def generate_location_description(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует описание локации"""
        try:
            prompt = self._build_location_prompt(case, location, discovered_evidence)

            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2048,
                temperature=0.6,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content

        except Exception as e:
            logger.error(f"Error generating location description: {e}")
            raise

    async def evaluate_theory(
        self, case: Case, theory: str, evidence_ids: List[UUID]
    ) -> Dict[str, float]:
        """Оценивает теорию игрока"""
        try:
            prompt = self._build_theory_evaluation_prompt(case, theory, evidence_ids)

            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            return self._parse_theory_evaluation(response.content)

        except Exception as e:
            logger.error(f"Error evaluating theory: {e}")
            raise

    async def generate_hint(
        self, case: Case, current_progress: float, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует подсказку"""
        try:
            prompt = self._build_hint_prompt(
                case, current_progress, discovered_evidence
            )

            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=512,
                temperature=0.4,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content

        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            raise

    def _build_investigation_prompt(
        self,
        difficulty: int,
        theme: Optional[str],
        constraints: Optional[Dict[str, str]],
    ) -> str:
        """Формирует промпт для генерации расследования"""
        prompt = f"""
        Создай детективное расследование со следующими параметрами:
        - Сложность: {difficulty}/10
        - Тема: {theme if theme else 'любая подходящая'}
        
        Требования:
        1. Расследование должно быть логичным и разрешимым
        2. Должно включать несколько локаций
        3. В каждой локации должны быть улики
        4. Должна быть четкая цепочка улик и связей
        
        {self._format_constraints(constraints) if constraints else ''}
        
        Формат ответа должен быть структурированным и содержать все необходимые данные для создания объекта Case.
        """
        return prompt

    def _build_evidence_analysis_prompt(
        self, case: Case, evidence: Evidence, context: Optional[Dict[str, str]]
    ) -> str:
        """Формирует промпт для анализа улики"""
        prompt = f"""
        Проанализируй улику в контексте текущего расследования:
        
        Дело: {case.title}
        Описание дела: {case.description}
        
        Улика:
        - Тип: {evidence.type.value}
        - Описание: {evidence.description}
        - Место обнаружения: {evidence.location_found}
        
        {self._format_context(context) if context else ''}
        
        Предоставь детальный анализ улики, включая:
        1. Значимость для расследования
        2. Связи с другими уликами
        3. Возможные выводы
        """
        return prompt

    def _build_location_prompt(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> str:
        """Формирует промпт для описания локации"""
        evidence_desc = "\n".join(
            [f"- {ev.type.value}: {ev.description}" for ev in discovered_evidence]
        )

        prompt = f"""
        Создай атмосферное описание локации в контексте расследования:
        
        Локация: {location.name}
        Базовое описание: {location.description}
        Уровень риска: {location.risk_level}/10
        
        Найденные улики:
        {evidence_desc}
        
        Описание должно:
        1. Создавать напряженную атмосферу
        2. Включать детали, важные для расследования
        3. Намекать на возможные скрытые улики
        """
        return prompt

    def _build_theory_evaluation_prompt(
        self, case: Case, theory: str, evidence_ids: List[UUID]
    ) -> str:
        """Формирует промпт для оценки теории"""
        evidence = [ev for ev in case.evidence if ev.id in evidence_ids]
        evidence_desc = "\n".join(
            [f"- {ev.type.value}: {ev.description}" for ev in evidence]
        )

        prompt = f"""
        Оцени теорию игрока в контексте расследования:
        
        Теория:
        {theory}
        
        Использованные улики:
        {evidence_desc}
        
        Оцени следующие аспекты (0-1):
        1. Точность: насколько теория соответствует фактам
        2. Полнота: насколько учтены все важные улики
        3. Связность: насколько логично связаны элементы теории
        
        Ответ должен быть в формате JSON с полями accuracy, completeness, coherence.
        """
        return prompt

    def _build_hint_prompt(
        self, case: Case, current_progress: float, discovered_evidence: List[Evidence]
    ) -> str:
        """Формирует промпт для генерации подсказки"""
        evidence_desc = "\n".join(
            [f"- {ev.type.value}: {ev.description}" for ev in discovered_evidence]
        )

        prompt = f"""
        Создай подсказку для игрока в текущей ситуации:
        
        Прогресс: {current_progress * 100}%
        
        Найденные улики:
        {evidence_desc}
        
        Подсказка должна:
        1. Быть не слишком прямой
        2. Направлять в правильном направлении
        3. Учитывать текущий прогресс
        4. Основываться на найденных уликах
        """
        return prompt

    def _format_constraints(self, constraints: Dict[str, str]) -> str:
        """Форматирует ограничения для промпта"""
        if not constraints:
            return ""

        return "Дополнительные требования:\n" + "\n".join(
            [f"- {key}: {value}" for key, value in constraints.items()]
        )

    def _format_context(self, context: Dict[str, str]) -> str:
        """Форматирует контекст для промпта"""
        if not context:
            return ""

        return "Дополнительный контекст:\n" + "\n".join(
            [f"- {key}: {value}" for key, value in context.items()]
        )

    def _parse_investigation_response(self, response: str) -> Case:
        """Парсит ответ от Claude и создает объект Case"""
        try:
            import json
            import uuid
            from datetime import datetime

            # Парсим JSON ответ
            data = json.loads(response)

            # Создаем локации
            locations = [
                Location(
                    id=uuid.UUID(loc.get("id", str(uuid.uuid4()))),
                    name=loc["name"],
                    description=loc["description"],
                    coordinates=(loc["coordinates"]["lat"], loc["coordinates"]["lon"]),
                    risk_level=loc["risk_level"],
                    evidence_found=[],
                )
                for loc in data["locations"]
            ]

            # Создаем улики
            evidence = [
                Evidence(
                    id=uuid.UUID(ev.get("id", str(uuid.uuid4()))),
                    type=EvidenceType[ev["type"].upper()],
                    description=ev["description"],
                    location_found=ev["location_found"],
                    timestamp_found=datetime.fromisoformat(ev["timestamp_found"]),
                    analysis_results=ev.get("analysis_results"),
                    related_evidence_ids=(
                        [
                            uuid.UUID(rel_id)
                            for rel_id in ev.get("related_evidence_ids", [])
                        ]
                        if ev.get("related_evidence_ids")
                        else None
                    ),
                )
                for ev in data["evidence"]
            ]

            # Создаем объект Case
            case = Case(
                id=uuid.UUID(data.get("id", str(uuid.uuid4()))),
                title=data["title"],
                description=data["description"],
                status=CaseStatus[data["status"].upper()],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                difficulty=data["difficulty"],
                locations=locations,
                evidence=evidence,
                detective_notes=data.get("detective_notes", []),
                related_cases=(
                    [uuid.UUID(case_id) for case_id in data.get("related_cases", [])]
                    if data.get("related_cases")
                    else None
                ),
            )

            return case

        except Exception as e:
            logger.error(f"Error parsing investigation response: {e}")
            raise ValueError(f"Invalid investigation response format: {e}")

    def _parse_theory_evaluation(self, response: str) -> Dict[str, float]:
        """Парсит оценку теории"""
        try:
            import json

            data = json.loads(response)

            # Проверяем наличие всех необходимых полей
            required_fields = {"accuracy", "completeness", "coherence"}
            if not all(field in data for field in required_fields):
                raise ValueError(
                    "Missing required fields in theory evaluation response"
                )

            # Проверяем, что все значения в диапазоне [0, 1]
            for field in required_fields:
                value = data[field]
                if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                    raise ValueError(
                        f"Invalid value for {field}: must be between 0 and 1"
                    )

            return {
                "accuracy": float(data["accuracy"]),
                "completeness": float(data["completeness"]),
                "coherence": float(data["coherence"]),
            }

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding theory evaluation response: {e}")
            raise ValueError("Invalid JSON format in theory evaluation response")
        except Exception as e:
            logger.error(f"Error parsing theory evaluation: {e}")
            raise ValueError(f"Error parsing theory evaluation: {e}")


class ClaudeAIService(AIService):
    """Реализация AIService с использованием Claude AI."""

    def __init__(self, api_key: str):
        """
        Инициализация сервиса.

        Args:
            api_key: Ключ API для доступа к Claude AI
        """
        self.client = anthropic.Client(api_key=api_key)

    async def generate_case(self, difficulty: int = 5) -> Optional[Dict]:
        """Генерирует новое расследование."""
        prompt = f"""
        Сгенерируй детективное расследование сложности {difficulty} из 10.
        Включи следующие элементы:
        - Название дела
        - Описание преступления
        - Список подозреваемых (2-4 человека)
        - Список улик (3-6 предметов)
        - Список локаций (2-4 места)
        - Решение дела
        
        Формат ответа должен быть в виде JSON.
        """

        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content
        except Exception as e:
            print(f"Ошибка при генерации дела: {e}")
            return None

    async def analyze_evidence(
        self, case: Case, evidence: Evidence, context: Optional[Dict[str, str]] = None
    ) -> str:
        """Анализирует улику и предоставляет выводы."""
        prompt = f"""
        Проанализируй улику в контексте расследования:
        
        Дело:
        Название: {case.title}
        Описание: {case.description}
        
        Улика:
        Название: {evidence.title}
        Описание: {evidence.description}
        Местоположение: {evidence.location}
        Тип: {evidence.type.value if evidence.type else 'Не указан'}
        
        {f'Дополнительный контекст: {chr(10).join(f"{k}: {v}" for k, v in context.items())}' if context else ''}
        
        Предоставь детальный анализ улики и её значимость для расследования.
        """

        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content
        except Exception as e:
            print(f"Ошибка при анализе улики: {e}")
            return "Не удалось проанализировать улику"

    async def generate_location_description(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует описание локации с учетом найденных улик."""
        evidence_descriptions = "\n".join(
            f"- {e.title}: {e.description}" for e in discovered_evidence
        )

        prompt = f"""
        Опиши локацию в контексте расследования:
        
        Дело:
        Название: {case.title}
        Описание: {case.description}
        
        Локация:
        Название: {location.name}
        Описание: {location.description}
        
        Найденные улики:
        {evidence_descriptions}
        
        Создай атмосферное описание локации, включая важные детали для расследования.
        """

        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content
        except Exception as e:
            print(f"Ошибка при генерации описания локации: {e}")
            return "Не удалось сгенерировать описание локации"

    async def evaluate_theory(
        self, case: Case, theory: str, evidence_ids: List[UUID]
    ) -> Dict[str, float]:
        """Оценивает теорию игрока."""
        evidence_list = [e for e in case.evidence_ids if e in evidence_ids]
        evidence_descriptions = "\n".join(
            f"- {e.title}: {e.description}" for e in evidence_list
        )

        prompt = f"""
        Оцени теорию по делу:
        
        Дело:
        Название: {case.title}
        Описание: {case.description}
        
        Теория игрока:
        {theory}
        
        Использованные улики:
        {evidence_descriptions}
        
        Оцени теорию по следующим критериям (0-1):
        - Точность: насколько теория соответствует фактам
        - Полнота: насколько теория объясняет все улики
        - Связность: насколько логично и последовательно изложена теория
        
        Ответ должен быть в формате JSON.
        """

        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content
        except Exception as e:
            print(f"Ошибка при оценке теории: {e}")
            return {"accuracy": 0.0, "completeness": 0.0, "coherence": 0.0}

    async def generate_hint(
        self, case: Case, current_progress: float, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует подсказку для игрока."""
        evidence_descriptions = "\n".join(
            f"- {e.title}: {e.description}" for e in discovered_evidence
        )

        prompt = f"""
        Сгенерируй подсказку для расследования:
        
        Дело:
        Название: {case.title}
        Описание: {case.description}
        
        Прогресс расследования: {current_progress * 100}%
        
        Найденные улики:
        {evidence_descriptions}
        
        Создай неявную подсказку, которая направит игрока в правильном направлении,
        но не раскроет решение напрямую.
        """

        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=300,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content
        except Exception as e:
            print(f"Ошибка при генерации подсказки: {e}")
            return "Не удалось сгенерировать подсказку"

    async def analyze_suspect(
        self, case: Case, suspect: Suspect, evidence: List[Evidence]
    ) -> Dict[str, str]:
        """Анализирует подозреваемого."""
        evidence_descriptions = "\n".join(
            f"- {e.title}: {e.description}" for e in evidence
        )

        prompt = f"""
        Проанализируй подозреваемого:
        
        Дело:
        Название: {case.title}
        Описание: {case.description}
        
        Подозреваемый:
        Имя: {suspect.name}
        Описание: {suspect.description}
        Алиби: {suspect.alibi}
        Мотив: {suspect.motive}
        
        Связанные улики:
        {evidence_descriptions}
        
        Проведи анализ и предоставь:
        - Оценку правдоподобности алиби
        - Анализ мотива
        - Связь с уликами
        - Общую оценку подозрительности
        
        Ответ должен быть в формате JSON.
        """

        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=800,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content
        except Exception as e:
            print(f"Ошибка при анализе подозреваемого: {e}")
            return {
                "alibi_credibility": "Не удалось оценить",
                "motive_analysis": "Не удалось проанализировать",
                "evidence_connection": "Не удалось установить",
                "suspicion_level": "Не удалось определить",
            }

    async def generate_interrogation(
        self, case: Case, suspect: Suspect, evidence: List[Evidence]
    ) -> List[Dict[str, str]]:
        """Генерирует диалог допроса."""
        evidence_descriptions = "\n".join(
            f"- {e.title}: {e.description}" for e in evidence
        )

        prompt = f"""
        Сгенерируй диалог допроса:
        
        Дело:
        Название: {case.title}
        Описание: {case.description}
        
        Подозреваемый:
        Имя: {suspect.name}
        Описание: {suspect.description}
        Алиби: {suspect.alibi}
        Мотив: {suspect.motive}
        
        Улики для использования:
        {evidence_descriptions}
        
        Создай диалог допроса с 5-7 вопросами и ответами.
        Ответы должны быть правдоподобными и соответствовать характеру подозреваемого.
        Формат ответа должен быть в виде списка JSON объектов с полями "question" и "answer".
        """

        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content
        except Exception as e:
            print(f"Ошибка при генерации допроса: {e}")
            return [{"question": "Ошибка", "answer": "Не удалось сгенерировать допрос"}]
