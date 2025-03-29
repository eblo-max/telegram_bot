from typing import List, Optional
from uuid import UUID
from datetime import datetime
import logging
import uuid
import json

from dark_archive.domain.interfaces.case_repository import ICaseRepository
from dark_archive.domain.interfaces.llm_client import ILLMClient
from dark_archive.domain.models.case import Case, Evidence, Location

logger = logging.getLogger(__name__)


class CaseService:
    """Сервис для работы с расследованиями"""

    def __init__(self, case_repository: ICaseRepository, llm_client: ILLMClient):
        self._repository = case_repository
        self._llm_client = llm_client
        logger.info("CaseService initialized")

    async def create_case(self, difficulty: int = 5) -> Optional[Case]:
        """Создает новое расследование"""
        try:
            logger.info(f"Creating new case with difficulty {difficulty}")
            logger.debug(f"Using AI service: {self._llm_client.__class__.__name__}")

            # Генерируем данные для расследования
            prompt = self._build_case_generation_prompt(difficulty)
            response = await self._llm_client.analyze_text(
                text="", instruction=prompt, context={"difficulty": str(difficulty)}
            )

            if not response:
                logger.error("Failed to generate case data")
                return None

            # Создаем объект расследования
            case = Case.create(
                title=response["title"],
                description=response["description"],
                difficulty=difficulty,
                initial_location=Location.create(
                    name=response["initial_location"]["name"],
                    description=response["initial_location"]["description"],
                    risk_level=response["initial_location"]["risk_level"],
                ),
            )

            # Добавляем локации и улики
            for loc_data in response["locations"]:
                location = Location.create(
                    name=loc_data["name"],
                    description=loc_data["description"],
                    risk_level=loc_data["risk_level"],
                )

                for ev_data in loc_data["evidence"]:
                    evidence = Evidence.create(
                        name=ev_data["name"],
                        description=ev_data["description"],
                        type=ev_data["type"],
                        importance=ev_data["importance"],
                    )
                    location.add_evidence(evidence)

                case.add_location(location)

            # Сохраняем в репозиторий
            logger.debug(f"Saving case to repository: {case.id}")
            await self._repository.create(case)
            logger.info(f"Created new case: {case.title}")
            return case

        except Exception as e:
            logger.error(f"Error creating case: {str(e)}")
            return None

    async def get_case(self, case_id: UUID) -> Optional[Case]:
        """Получает расследование по ID"""
        try:
            logger.debug(f"Getting case with ID: {case_id}")
            case = await self._repository.get_by_id(case_id)
            if case:
                logger.info(f"Case found: {case_id}")
            else:
                logger.info(f"Case not found: {case_id}")
            return case
        except Exception as e:
            logger.error(f"Error getting case {case_id}: {str(e)}")
            return None

    async def list_cases(self, user_id: Optional[int] = None) -> List[Case]:
        """Получает список дел"""
        try:
            logger.debug(f"Listing cases for user: {user_id if user_id else 'all'}")
            if user_id:
                cases = await self._repository.get_by_user_id(user_id)
            else:
                cases = await self._repository.get_all()
            logger.info(f"Retrieved {len(cases)} cases")
            return cases
        except Exception as e:
            logger.error(f"Error listing cases: {e}", exc_info=True)
            return []

    async def analyze_evidence(self, case: Case, evidence: Evidence) -> Optional[str]:
        """Анализирует улику"""
        try:
            logger.debug(f"Analyzing evidence {evidence.id} for case {case.id}")
            context = {
                "case_title": case.title,
                "case_description": case.description,
                "location_name": (
                    evidence.location.name if evidence.location else "Unknown"
                ),
                "discovered_evidence": [
                    {"name": e.name, "description": e.description}
                    for e in case.discovered_evidence
                ],
            }

            response = await self._llm_client.generate_text(
                prompt=self._build_evidence_analysis_prompt(evidence),
                temperature=0.7,
                context=context,
            )

            logger.info(f"Evidence analysis completed for {evidence.id}")
            return response
        except Exception as e:
            logger.error(f"Error analyzing evidence: {str(e)}")
            return None

    async def generate_hint(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> Optional[str]:
        """Генерирует подсказку для локации"""
        try:
            logger.debug(f"Generating hint for case {case.id}, location {location.id}")
            hint = await self._llm_client.generate_text(
                prompt=self._build_hint_prompt(case, location, discovered_evidence),
                temperature=0.8,
                context={
                    "case_title": case.title,
                    "case_description": case.description,
                    "discovered_evidence": [
                        {"name": e.name, "description": e.description}
                        for e in discovered_evidence
                    ],
                },
            )
            logger.info(f"Hint generated for location {location.id}")
            return hint
        except Exception as e:
            logger.error(f"Error generating hint: {e}", exc_info=True)
            return "Ошибка при генерации подсказки"

    async def evaluate_theory(
        self, case: Case, theory: str, evidence_ids: List[UUID]
    ) -> dict:
        """Оценивает теорию игрока"""
        try:
            logger.debug(f"Evaluating theory for case {case.id}")
            result = await self._llm_client.evaluate_theory(case, theory, evidence_ids)
            logger.info(f"Theory evaluation completed for case {case.id}")
            return result
        except Exception as e:
            logger.error(f"Error evaluating theory: {e}", exc_info=True)
            return {"accuracy": 0.0, "completeness": 0.0, "coherence": 0.0}

    async def generate_location_description(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> Optional[str]:
        """Генерирует описание локации"""
        try:
            logger.debug(
                f"Generating description for location {location.id} in case {case.id}"
            )
            context = {
                "case_title": case.title,
                "case_description": case.description,
                "discovered_evidence": [
                    {"name": e.name, "description": e.description}
                    for e in discovered_evidence
                ],
            }

            response = await self._llm_client.generate_text(
                prompt=self._build_location_prompt(location),
                temperature=0.8,
                context=context,
            )

            logger.info(f"Description generated for location {location.id}")
            return response
        except Exception as e:
            logger.error(f"Error generating location description: {str(e)}")
            return None

    async def generate_evidence_description(
        self, case: Case, evidence: Evidence, discovered_evidence: List[Evidence]
    ) -> str:
        """Генерирует описание улики с учетом контекста дела"""
        try:
            logger.debug(f"Generating description for evidence {evidence.id}")
            description = await self._llm_client.analyze_evidence(
                case,
                evidence,
                {"discovered_evidence": [e.id for e in discovered_evidence]},
            )
            logger.info(f"Description generated for evidence {evidence.id}")
            return description
        except Exception as e:
            logger.error(f"Error generating evidence description: {e}", exc_info=True)
            return evidence.description

    def _build_case_generation_prompt(self, difficulty: int) -> str:
        """Формирует промпт для генерации расследования"""
        return f"""
        Create a new investigation case with the following requirements:
        - Difficulty level: {difficulty} (1-10)
        - Include a title and description
        - Create an initial location
        - Generate 2-4 additional locations
        - Each location should have 1-3 pieces of evidence
        - Each location should have a risk level (1-10)
        
        Return the data in the following JSON format:
        {{
            "title": "Case title",
            "description": "Case description",
            "initial_location": {{
                "name": "Location name",
                "description": "Location description",
                "risk_level": 5
            }},
            "locations": [
                {{
                    "name": "Location name",
                    "description": "Location description",
                    "risk_level": 5,
                    "evidence": [
                        {{
                            "name": "Evidence name",
                            "description": "Evidence description",
                            "type": "physical|digital|forensic|witness|occult",
                            "importance": 5
                        }}
                    ]
                }}
            ]
        }}
        """

    def _build_evidence_analysis_prompt(self, evidence: Evidence) -> str:
        """Формирует промпт для анализа улики"""
        return f"""
        Analyze the following evidence:
        Name: {evidence.name}
        Description: {evidence.description}
        Type: {evidence.type}
        Importance: {evidence.importance}

        Provide a detailed analysis considering:
        1. Physical characteristics
        2. Potential significance
        3. Possible connections to the case
        4. Recommended next steps
        """

    def _build_location_prompt(self, location: Location) -> str:
        """Формирует промпт для описания локации"""
        return f"""
        Describe the following location in detail:
        Name: {location.name}
        Base description: {location.description}
        Risk level: {location.risk_level}

        Provide an atmospheric and detailed description that includes:
        1. Visual details
        2. Ambient sounds and smells
        3. Notable features
        4. Potential areas of interest
        5. Signs of recent activity
        """

    def _build_hint_prompt(
        self, case: Case, location: Location, discovered_evidence: List[Evidence]
    ) -> str:
        """Формирует промпт для генерации подсказки"""
        return f"""
        Generate a hint for the following location:
        Name: {location.name}
        Description: {location.description}
        Risk level: {location.risk_level}

        Discovered evidence:
        {", ".join([f"{e.name}: {e.description}" for e in discovered_evidence])}

        Provide a concise and relevant hint that helps the detective understand the location better.
        """
