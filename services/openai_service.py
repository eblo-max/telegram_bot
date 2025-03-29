import json
import logging
from typing import Dict, List, Optional
from uuid import UUID

from openai import AsyncOpenAI

from dark_archive.application.interfaces.ai_service import IAIService
from dark_archive.domain.models.case import Case, Evidence, Location

logger = logging.getLogger(__name__)


class OpenAIService(IAIService):
    """Реализация AI сервиса с использованием OpenAI API"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_case(self, difficulty: int) -> Dict:
        """Генерирует новое расследование используя OpenAI"""
        try:
            prompt = f"""
            Сгенерируй детективное расследование сложности {difficulty} (1-10).
            Расследование должно включать:
            - Название и описание дела
            - Начальную локацию с описанием и уровнем риска
            - 2-4 дополнительные локации, каждая с:
              - Названием и описанием
              - Уровнем риска (1-10)
              - 1-3 уликами, у каждой:
                - Название
                - Описание
                - Тип (документ/предмет/след/запись)
                - Важность (1-10)
            
            Верни результат в формате JSON:
            {{
                "title": str,
                "description": str,
                "initial_location": {{
                    "name": str,
                    "description": str,
                    "risk_level": int
                }},
                "locations": [
                    {{
                        "name": str,
                        "description": str,
                        "risk_level": int,
                        "evidence": [
                            {{
                                "name": str,
                                "description": str,
                                "type": str,
                                "importance": int
                            }}
                        ]
                    }}
                ]
            }}
            """

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - генератор детективных расследований. Создавай атмосферные и логичные дела.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"Generated case: {result['title']}")
            return result

        except Exception as e:
            logger.error(f"Error generating case: {e}")
            raise

    async def analyze_evidence(self, case: Case, evidence: Evidence) -> Optional[str]:
        """Анализирует улику и возвращает результаты анализа"""
        try:
            prompt = f"""
            Проанализируй улику в контексте расследования:
            
            Дело: {case.title}
            Описание дела: {case.description}
            
            Улика:
            Название: {evidence.name}
            Описание: {evidence.description}
            Тип: {evidence.type}
            Важность: {evidence.importance}
            
            Дай краткий анализ улики и её значения для расследования.
            """

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - опытный детектив. Анализируй улики профессионально и точно.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            analysis = response.choices[0].message.content
            logger.info(f"Generated evidence analysis for {evidence.name}")
            return analysis

        except Exception as e:
            logger.error(f"Error analyzing evidence: {e}")
            return None

    async def generate_hint(
        self, case: Case, progress: float, discovered_evidence: List[Evidence]
    ) -> Optional[str]:
        """Генерирует подсказку на основе текущего прогресса расследования"""
        try:
            evidence_info = "\n".join(
                [
                    f"- {e.name}: {e.description} (важность: {e.importance})"
                    for e in discovered_evidence
                ]
            )

            prompt = f"""
            Дай подсказку для расследования:
            
            Дело: {case.title}
            Описание: {case.description}
            Текущий прогресс: {progress * 100}%
            
            Найденные улики:
            {evidence_info}
            
            Сгенерируй краткую подсказку, которая поможет продвинуться в расследовании,
            основываясь на текущем прогрессе и найденных уликах.
            """

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - опытный детектив. Давай полезные, но не слишком прямые подсказки.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            hint = response.choices[0].message.content
            logger.info(f"Generated hint for case {case.title}")
            return hint

        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return None

    async def generate_location_description(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует описание локации с учетом найденных улик"""
        try:
            evidence_info = "\n".join(
                [f"- {e.name}: {e.description}" for e in discovered_evidence]
            )

            prompt = f"""
            Сгенерируй атмосферное описание локации с учетом найденных улик:
            
            Дело: {case.title}
            Описание дела: {case.description}
            
            Локация: {location.name}
            Базовое описание: {location.description}
            Уровень риска: {location.risk_level}
            
            Найденные улики:
            {evidence_info if evidence_info else "Улики пока не найдены"}
            
            Опиши, как выглядит локация сейчас, учитывая найденные улики и общий контекст дела.
            """

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - атмосферный писатель. Создавай детальные и напряженные описания локаций.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            description = response.choices[0].message.content
            logger.info(f"Generated location description for {location.name}")
            return description

        except Exception as e:
            logger.error(f"Error generating location description: {e}")
            return location.description

    async def evaluate_theory(
        self, case: Case, theory: str, evidence_ids: List[UUID]
    ) -> Dict[str, float]:
        """Оценивает теорию игрока"""
        try:
            # Получаем улики по ID
            evidence_list = []
            for location in case.locations:
                for evidence in location.evidence:
                    if evidence.id in evidence_ids:
                        evidence_list.append(evidence)

            evidence_info = "\n".join(
                [
                    f"- {e.name}: {e.description} (важность: {e.importance})"
                    for e in evidence_list
                ]
            )

            prompt = f"""
            Оцени теорию игрока в контексте расследования:
            
            Дело: {case.title}
            Описание дела: {case.description}
            
            Теория игрока:
            {theory}
            
            Использованные улики:
            {evidence_info}
            
            Оцени теорию по следующим критериям (0.0 - 1.0):
            1. Точность - насколько теория соответствует фактам
            2. Полнота - насколько теория объясняет все улики
            3. Связность - насколько логично и последовательно выстроена теория
            
            Верни оценки в формате JSON:
            {{
                "accuracy": float,
                "completeness": float,
                "coherence": float
            }}
            """

            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - опытный детектив. Оценивай теории объективно и профессионально.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            logger.info(f"Evaluated theory for case {case.title}")
            return result

        except Exception as e:
            logger.error(f"Error evaluating theory: {e}")
            return {"accuracy": 0.0, "completeness": 0.0, "coherence": 0.0}
