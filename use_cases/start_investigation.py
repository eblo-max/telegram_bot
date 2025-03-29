# Created by setup script

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.exceptions import (
    PlayerNotFoundError,
    CaseNotFoundError,
    AccessDeniedError,
    CaseAlreadySolvedError,
    CaseAlreadyStartedError,
    CaseAlreadyInProgressError,
)


@dataclass
class StartInvestigationCommand:
    """Команда для начала расследования."""

    player_id: str
    case_id: str
    notes: Optional[str] = None


@dataclass
class StartInvestigationRequest:
    """Запрос на начало расследования."""

    case: Case


@dataclass
class StartInvestigationResponse:
    """Ответ на запрос начала расследования."""

    case: Case


class StartInvestigationUseCase:
    """Use case для начала расследования дела."""

    def __init__(self, player_repository, case_repository):
        self.player_repository = player_repository
        self.case_repository = case_repository

    async def execute(
        self, request: StartInvestigationRequest
    ) -> StartInvestigationResponse:
        """
        Выполняет начало расследования.

        Args:
            request: Запрос на начало расследования

        Returns:
            Ответ с обновленным делом

        Raises:
            CaseNotFoundError: Если дело не найдено
            CaseAlreadyStartedError: Если расследование уже начато
            CaseAlreadyInProgressError: Если дело уже в процессе расследования
        """
        if not request.case:
            raise CaseNotFoundError("Дело не найдено")

        if request.case.status == "in_progress":
            raise CaseAlreadyStartedError("Расследование уже начато")

        if request.case.status == "in_progress":
            raise CaseAlreadyInProgressError("Дело уже в процессе расследования")

        request.case.status = "in_progress"
        request.case.started_at = datetime.now()

        return StartInvestigationResponse(case=request.case)
