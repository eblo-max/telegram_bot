import json
import logging
from typing import Dict, List, Optional
from uuid import UUID
from dark_archive.application.interfaces.ai_service import IAIService
from dark_archive.domain.models.case import Case, Evidence, Location, CaseStatus
from dark_archive.domain.services.prompt_generator import PromptGenerator
import uuid
from dark_archive.infrastructure.ai.claude import ClaudeClient, ClaudeConfig

logger = logging.getLogger(__name__)

INVESTIGATION_PROMPT = """
Ты - генератор детективных расследований для игры Dark Archive. Создай новое расследование со следующими параметрами:

Сложность: {difficulty}/10
Тема: {theme}
Дополнительные требования: {constraints}

Расследование должно включать:
1. Основное описание дела
2. Список подозреваемых
3. Список улик и их местонахождение
4. Правильную теорию решения
5. Ложные следы

Формат ответа должен быть в JSON:
{
    "title": "Название дела",
    "description": "Описание дела",
    "difficulty": число,
    "locations": [
        {
            "name": "Название локации",
            "description": "Описание локации",
            "risk_level": число от 1 до 5,
            "coordinates": [широта, долгота]
        }
    ],
    "evidence": [
        {
            "title": "Название улики",
            "description": "Описание улики",
            "location_name": "Название локации где находится улика",
            "importance": число от 1 до 5
        }
    ],
    "solution": "Полное описание решения дела",
    "false_leads": ["Список ложных следов"]
}
"""


class ClaudeService(IAIService):
    """Сервис для работы с CLAUDE API"""

    def __init__(self, api_key: str):
        """Инициализация сервиса

        Args:
            api_key: Ключ API для доступа к CLAUDE
        """
        config = ClaudeConfig(api_key=api_key)
        self.ai_client = ClaudeClient(api_key=api_key)
        self.prompt_generator = PromptGenerator()
        logger.info("ClaudeService initialized")

    async def _generate_response(self, prompt: str, **kwargs) -> Optional[str]:
        try:
            return await self.ai_client.generate_text(
                prompt=prompt,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                context=kwargs.get("context"),
            )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None

    async def generate_investigation(
        self,
        difficulty: int,
        theme: Optional[str] = None,
        constraints: Optional[Dict[str, str]] = None,
    ) -> Case:
        """Генерирует новое расследование"""
        try:
            prompt = INVESTIGATION_PROMPT.format(
                difficulty=difficulty,
                theme=theme or "любая",
                constraints=(
                    json.dumps(constraints, ensure_ascii=False)
                    if constraints
                    else "нет"
                ),
            )

            message = await self._generate_response(prompt, json_response=True)

            if not message:
                logger.error("Empty response from Claude API")
                return self._get_default_case()

            try:
                case_data = json.loads(message)
                # Создаем локации
                locations = [
                    Location(
                        name=loc["name"],
                        description=loc["description"],
                        coordinates=tuple(loc["coordinates"]),
                        risk_level=loc["risk_level"],
                    )
                    for loc in case_data["locations"]
                ]

                # Создаем улики
                evidence = [
                    Evidence(
                        title=ev["title"],
                        description=ev["description"],
                        location_name=ev["location_name"],
                        importance=ev["importance"],
                    )
                    for ev in case_data["evidence"]
                ]

                # Создаем дело
                case = Case(
                    title=case_data["title"],
                    description=case_data["description"],
                    difficulty=case_data["difficulty"],
                    status=CaseStatus.ACTIVE,
                    locations=locations,
                    evidence=evidence,
                    solution=case_data["solution"],
                    false_leads=case_data["false_leads"],
                )

                logger.info(f"Generated new investigation: {case.title}")
                return case

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude API response: {e}")
                return self._get_default_case()

        except Exception as e:
            logger.error(f"Error generating investigation: {e}")
            raise

    async def analyze_evidence(
        self, case: Case, evidence: Evidence, context: Optional[Dict[str, str]] = None
    ) -> str:
        """Анализирует улику"""
        try:
            prompt = f"""
            Проанализируй улику в контексте текущего расследования:

            Дело: {case.title}
            Описание дела: {case.description}

            Улика: {evidence.title}
            Описание улики: {evidence.description}
            Найдена в: {evidence.location_name}

            Дополнительный контекст: {json.dumps(context, ensure_ascii=False) if context else "нет"}

            Предоставь детальный анализ улики и её значение для расследования.
            """

            message = await self._generate_response(prompt)

            return message

        except Exception as e:
            logger.error(f"Error analyzing evidence: {e}")
            raise

    async def generate_location_description(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует описание локации"""
        try:
            evidence_desc = "\n".join(
                [f"- {ev.title}: {ev.description}" for ev in discovered_evidence]
            )

            prompt = f"""
            Опиши локацию в контексте текущего расследования:

            Дело: {case.title}
            Локация: {location.name}
            Базовое описание: {location.description}
            Уровень риска: {location.risk_level}/5

            Найденные улики:
            {evidence_desc}

            Создай атмосферное и детальное описание локации, учитывая найденные улики и контекст расследования.
            """

            message = await self._generate_response(prompt)

            return message

        except Exception as e:
            logger.error(f"Error generating location description: {e}")
            raise

    async def evaluate_theory(
        self, case: Case, theory: str, evidence_ids: List[UUID]
    ) -> Dict[str, float]:
        """Оценивает теорию игрока"""
        try:
            # Получаем улики по ID
            used_evidence = [ev for ev in case.evidence if ev.id in evidence_ids]

            evidence_desc = "\n".join(
                [f"- {ev.title}: {ev.description}" for ev in used_evidence]
            )

            prompt = f"""
            Оцени теорию игрока в контексте расследования:

            Дело: {case.title}
            Описание дела: {case.description}

            Правильное решение: {case.solution}

            Теория игрока: {theory}

            Использованные улики:
            {evidence_desc}

            Оцени теорию по следующим критериям (0-1):
            1. Точность - насколько теория соответствует реальному решению
            2. Полнота - насколько полно использованы улики и учтены все аспекты дела
            3. Связность - насколько логично связаны улики и выводы

            Ответ должен быть в формате JSON:
            {{
                "accuracy": float,
                "completeness": float,
                "coherence": float
            }}
            """

            message = await self._generate_response(prompt)

            return json.loads(message)

        except Exception as e:
            logger.error(f"Error evaluating theory: {e}")
            raise

    async def generate_hint(
        self, case: Case, current_progress: float, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует подсказку для игрока"""
        try:
            evidence_desc = "\n".join(
                [f"- {ev.title}: {ev.description}" for ev in discovered_evidence]
            )

            prompt = f"""
            Создай подсказку для игрока в контексте расследования:

            Дело: {case.title}
            Описание дела: {case.description}
            Текущий прогресс: {current_progress * 100}%

            Найденные улики:
            {evidence_desc}

            Создай неявную подсказку, которая поможет игроку продвинуться в расследовании,
            но не раскроет решение напрямую. Учитывай текущий прогресс и найденные улики.
            """

            message = await self._generate_response(prompt)

            return message

        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            raise

    async def generate_case(self, difficulty: int = 5) -> Dict:
        """Генерирует новое дело с помощью AI"""
        try:
            prompt = """
            Сгенерируй детективное расследование в формате JSON со следующими полями:
            - title: название дела
            - description: описание дела
            - difficulty: число от 1 до 10
            - locations: массив с локациями, где каждая локация содержит:
              - name: название локации
              - description: описание локации
              - risk_level: уровень риска (0.0-1.0)
              - evidence: массив улик в локации
            """

            response = await self.ai_client.generate_text(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7,
            )

            logger.debug(f"AI response: {response}")

            try:
                case_data = json.loads(response)
                logger.info(f"Successfully parsed case data: {list(case_data.keys())}")
                return case_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.debug(f"Response content: {response[:200]}...")
                return self._get_default_case()

        except Exception as e:
            logger.error(f"Error generating case: {e}", exc_info=True)
            return self._get_default_case()

    def _get_default_case(self) -> Dict:
        """Возвращает структуру дела по умолчанию в случае ошибки"""
        return {
            "title": "Новое расследование",
            "description": "Детали дела уточняются...",
            "difficulty": 5,
            "locations": [
                {
                    "name": "Начальная локация",
                    "description": "Исходная точка расследования",
                    "risk_level": 0.1,
                    "evidence": [],
                }
            ],
        }
