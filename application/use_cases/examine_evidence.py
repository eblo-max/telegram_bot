# Created by setup script

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.repositories.player_repository import PlayerRepository
from dark_archive.domain.repositories.case_repository import CaseRepository
from dark_archive.domain.repositories.evidence_repository import EvidenceRepository
from dark_archive.domain.exceptions import (
    PlayerNotFoundError,
    CaseNotFoundError,
    EvidenceNotFoundError,
    AccessDeniedError,
    EvidenceAlreadyExaminedError,
)


@dataclass
class ExamineEvidenceCommand:
    """Команда для исследования улики."""

    player_id: str
    case_id: str
    evidence_id: str
    notes: Optional[str] = None


@dataclass
class ExamineEvidenceRequest:
    """Запрос на осмотр улики."""

    evidence: Evidence
    notes: Optional[str] = None


@dataclass
class ExamineEvidenceResponse:
    """Ответ с обновленной уликой."""

    evidence: Evidence


class ExamineEvidenceUseCase:
    """Use case для осмотра улики."""

    def __init__(
        self,
        player_repository: PlayerRepository,
        case_repository: CaseRepository,
        evidence_repository: EvidenceRepository,
    ):
        """
        Инициализирует use case.

        Args:
            player_repository: Репозиторий игроков
            case_repository: Репозиторий дел
            evidence_repository: Репозиторий улик
        """
        self.player_repository = player_repository
        self.case_repository = case_repository
        self.evidence_repository = evidence_repository

    async def execute(self, command: ExamineEvidenceCommand) -> ExamineEvidenceResponse:
        """
        Выполняет осмотр улики.

        Args:
            command: Команда на осмотр улики

        Returns:
            Ответ с обновленной уликой

        Raises:
            PlayerNotFoundError: Если игрок не найден
            CaseNotFoundError: Если дело не найдено
            EvidenceNotFoundError: Если улика не найдена
            AccessDeniedError: Если у игрока нет доступа к делу
            EvidenceAlreadyExaminedError: Если улика уже была осмотрена
        """
        # Получаем игрока
        player = await self.player_repository.get_by_id(command.player_id)
        if not player:
            raise PlayerNotFoundError(command.player_id)

        # Получаем дело
        case = await self.case_repository.get_by_id(command.case_id)
        if not case:
            raise CaseNotFoundError(command.case_id)

        # Проверяем доступ
        if not player.has_access_to_case(case):
            raise AccessDeniedError()

        # Получаем улику
        evidence = await self.evidence_repository.get_by_id(command.evidence_id)
        if not evidence:
            raise EvidenceNotFoundError(command.evidence_id)

        # Проверяем, не была ли улика уже осмотрена
        if evidence.examined:
            raise EvidenceAlreadyExaminedError(evidence.id)

        # Осматриваем улику
        evidence.examine(command.notes)

        # Сохраняем изменения
        await self.evidence_repository.save(evidence)

        return ExamineEvidenceResponse(evidence=evidence)

    def execute_sync(self, request: ExamineEvidenceRequest) -> ExamineEvidenceResponse:
        """
        Выполняет осмотр улики синхронно.

        Args:
            request: Запрос на осмотр улики

        Returns:
            Ответ с обновленной уликой

        Raises:
            EvidenceNotFoundError: Если улика не найдена
            EvidenceAlreadyExaminedError: Если улика уже была осмотрена
        """
        if not request.evidence:
            raise EvidenceNotFoundError("evidence")

        if request.evidence.examined:
            raise EvidenceAlreadyExaminedError(request.evidence.id)

        request.evidence.examine(request.notes)

        return ExamineEvidenceResponse(evidence=request.evidence)
