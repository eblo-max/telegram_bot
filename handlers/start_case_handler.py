from dataclasses import dataclass
from typing import Optional

from dark_archive.application.commands.start_case_command import (
    StartCaseCommand,
    StartCaseResult,
)
from dark_archive.application.interfaces.command_handler import CommandHandler
from dark_archive.application.interfaces.repository import Repository
from dark_archive.domain.services.case_service import CaseService


@dataclass
class StartCaseHandler(CommandHandler[StartCaseCommand, StartCaseResult]):
    """Обработчик команды начала расследования."""

    repository: Repository
    service: CaseService

    async def handle(self, command: StartCaseCommand) -> StartCaseResult:
        """Обрабатывает команду начала расследования."""
        # Получаем игрока
        player = await self.repository.get(command.player_id)
        if not player:
            raise ValueError("Player not found")

        # Проверяем, нет ли уже активного расследования
        if player.active_case_id:
            raise ValueError("Player already has an active case")

        # Создаем новое дело
        case = await self.service.create_new_case()

        # Начинаем расследование
        player.start_case(case.id)
        await self.repository.update(player)

        return StartCaseResult(player_id=player.id, case_id=case.id)
