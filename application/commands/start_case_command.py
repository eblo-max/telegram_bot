# Created by setup script

from dataclasses import dataclass
from uuid import UUID

from dark_archive.application.interfaces.command_handler import TCommand


@dataclass
class StartCaseCommand(TCommand):
    """Команда для начала нового расследования."""

    player_id: UUID


@dataclass
class StartCaseResult:
    """Результат выполнения команды начала расследования."""

    player_id: UUID
    case_id: UUID
