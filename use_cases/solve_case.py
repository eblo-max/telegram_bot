# Created by setup script

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.enums import CaseStatus, PlayerRole
from dark_archive.domain.exceptions import (
    PlayerNotFoundError,
    CaseNotFoundError,
    SuspectNotFoundError,
    AccessDeniedError,
    InvalidSolutionError,
    CaseAlreadySolvedError,
)
from dark_archive.domain.repositories.case_repository import CaseRepository
from dark_archive.domain.repositories.player_repository import PlayerRepository


@dataclass
class SolveCaseCommand:
    """Команда для решения дела."""

    player_id: str
    case_id: str
    solution: str


@dataclass
class SolveCaseRequest:
    """Запрос на решение дела."""

    case: Case
    solution: str


@dataclass
class SolveCaseResponse:
    """Ответ с обновленным делом."""

    case: Case


class SolveCaseUseCase:
    """Use case для решения дела."""

    def __init__(
        self,
        player_repository: PlayerRepository,
        case_repository: CaseRepository,
    ):
        """
        Инициализирует use case.

        Args:
            player_repository: Репозиторий игроков
            case_repository: Репозиторий дел
        """
        self.player_repository = player_repository
        self.case_repository = case_repository

    async def execute(self, command: SolveCaseCommand) -> SolveCaseResponse:
        """
        Выполняет решение дела.

        Args:
            command: Команда на решение дела

        Returns:
            Ответ с обновленным делом

        Raises:
            PlayerNotFoundError: Если игрок не найден
            CaseNotFoundError: Если дело не найдено
            AccessDeniedError: Если у игрока нет доступа к делу
            CaseAlreadySolvedError: Если дело уже решено
            InvalidSolutionError: Если решение невалидно
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

        # Проверяем, не решено ли дело
        if case.status == CaseStatus.SOLVED:
            raise CaseAlreadySolvedError(case.id)

        # Проверяем валидность решения
        if not command.solution.strip():
            raise InvalidSolutionError()

        # Решаем дело
        case.solve(command.solution)
        player.complete_case(case.id)

        # Сохраняем изменения
        await self.case_repository.save(case)
        await self.player_repository.save(player)

        return SolveCaseResponse(case=case)

    def execute_sync(self, request: SolveCaseRequest) -> SolveCaseResponse:
        """
        Выполняет решение дела синхронно.

        Args:
            request: Запрос на решение дела

        Returns:
            Ответ с обновленным делом

        Raises:
            CaseNotFoundError: Если дело не найдено
            CaseAlreadySolvedError: Если дело уже решено
            InvalidSolutionError: Если решение невалидно
        """
        if not request.case:
            raise CaseNotFoundError("case")

        if request.case.status == CaseStatus.SOLVED:
            raise CaseAlreadySolvedError(request.case.id)

        if not request.solution.strip():
            raise InvalidSolutionError()

        request.case.solve(request.solution)

        return SolveCaseResponse(case=request.case)
