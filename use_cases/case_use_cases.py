from dataclasses import dataclass
from typing import List, Optional

from dark_archive.domain.entities.case import Case
from dark_archive.domain.exceptions import CaseNotFoundError
from dark_archive.application.interfaces.case_repository import ICaseRepository
from dark_archive.application.interfaces.ai_service import IAIService


@dataclass
class CreateCaseCommand:
    """Команда для создания нового дела"""

    title: str
    description: str
    difficulty: int


class CreateCaseUseCase:
    """Use case для создания нового дела"""

    def __init__(self, case_repository: ICaseRepository, ai_service: IAIService):
        self.case_repository = case_repository
        self.ai_service = ai_service

    async def execute(self, command: CreateCaseCommand) -> Case:
        case = Case(
            title=command.title,
            description=command.description,
            difficulty=command.difficulty,
        )
        await self.case_repository.save(case)
        return case


class GetCaseUseCase:
    """Use case для получения дела по ID"""

    def __init__(self, case_repository: ICaseRepository):
        self.case_repository = case_repository

    async def execute(self, case_id: str) -> Case:
        case = await self.case_repository.get_by_id(case_id)
        if not case:
            raise CaseNotFoundError(f"Case with id {case_id} not found")
        return case


class ListCasesUseCase:
    """Use case для получения списка дел"""

    def __init__(self, case_repository: ICaseRepository):
        self.case_repository = case_repository

    async def execute(self) -> List[Case]:
        return await self.case_repository.get_all()
