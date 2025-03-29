# Created by setup script

from dataclasses import dataclass
from uuid import UUID

from dark_archive.application.interfaces.query_handler import BaseQuery


@dataclass
class GetPlayerStatsQuery(BaseQuery):
    """Запрос для получения статистики игрока."""

    player_id: UUID


@dataclass
class PlayerStatsResult:
    """Результат запроса статистики игрока."""

    player_id: UUID
    reputation: int
    cases_solved: int
    evidence_collected: int
    theories_submitted: int
    achievements_count: int
    has_active_case: bool
