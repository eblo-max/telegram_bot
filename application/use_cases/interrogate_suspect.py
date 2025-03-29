# Created by setup script

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
import random

from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.enums import PlayerRole
from dark_archive.domain.exceptions import (
    PlayerNotFoundError,
    CaseNotFoundError,
    SuspectNotFoundError,
    AccessDeniedError,
    InvalidQuestionError,
    InterrogationCooldownError,
    SuspectInterrogationError,
)
from dark_archive.domain.repositories.case_repository import CaseRepository
from dark_archive.domain.repositories.player_repository import PlayerRepository
from dark_archive.domain.repositories.suspect_repository import SuspectRepository


@dataclass
class InterrogateSuspectRequest:
    """Запрос на допрос подозреваемого."""

    suspect: Suspect
    notes: Optional[str] = None


@dataclass
class InterrogateSuspectResponse:
    """Ответ с обновленным подозреваемым."""

    suspect: Suspect


@dataclass
class InterrogateSuspectCommand:
    """Команда для допроса подозреваемого."""

    player_id: str
    case_id: str
    suspect_id: str
    notes: Optional[str] = None


class InterrogateSuspectUseCase:
    """Use case для допроса подозреваемого."""

    def __init__(
        self,
        player_repository: PlayerRepository,
        case_repository: CaseRepository,
        suspect_repository: SuspectRepository,
    ):
        """
        Инициализирует use case.

        Args:
            player_repository: Репозиторий игроков
            case_repository: Репозиторий дел
            suspect_repository: Репозиторий подозреваемых
        """
        self.player_repository = player_repository
        self.case_repository = case_repository
        self.suspect_repository = suspect_repository

    async def execute(
        self, command: InterrogateSuspectCommand
    ) -> InterrogateSuspectResponse:
        """
        Выполняет допрос подозреваемого.

        Args:
            command: Команда на допрос подозреваемого

        Returns:
            Ответ с обновленным подозреваемым

        Raises:
            PlayerNotFoundError: Если игрок не найден
            CaseNotFoundError: Если дело не найдено
            SuspectNotFoundError: Если подозреваемый не найден
            AccessDeniedError: Если у игрока нет доступа к делу
            SuspectInterrogationError: Если подозреваемый не может быть допрошен
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

        # Получаем подозреваемого
        suspect = await self.suspect_repository.get_by_id(command.suspect_id)
        if not suspect:
            raise SuspectNotFoundError(command.suspect_id)

        # Проверяем возможность допроса
        if not suspect.can_be_interrogated():
            raise SuspectInterrogationError(suspect.id)

        # Допрашиваем подозреваемого
        suspect.interrogate(command.notes)

        # Сохраняем изменения
        await self.suspect_repository.save(suspect)

        return InterrogateSuspectResponse(suspect=suspect)

    def execute_sync(
        self, request: InterrogateSuspectRequest
    ) -> InterrogateSuspectResponse:
        """
        Выполняет допрос подозреваемого синхронно.

        Args:
            request: Запрос на допрос подозреваемого

        Returns:
            Ответ с обновленным подозреваемым

        Raises:
            SuspectNotFoundError: Если подозреваемый не найден
            SuspectInterrogationError: Если подозреваемый не может быть допрошен
        """
        if not request.suspect:
            raise SuspectNotFoundError("suspect")

        if not request.suspect.can_be_interrogated():
            raise SuspectInterrogationError(request.suspect.id)

        request.suspect.interrogate(request.notes)

        return InterrogateSuspectResponse(suspect=request.suspect)
