from dataclasses import dataclass
from uuid import UUID

from dark_archive.application.interfaces.query_handler import QueryHandler
from dark_archive.application.interfaces.repository import Repository
from dark_archive.application.queries.get_player_stats_query import (
    GetPlayerStatsQuery,
    PlayerStatsResult,
)


@dataclass
class GetPlayerStatsHandler(QueryHandler[GetPlayerStatsQuery, PlayerStatsResult]):
    """Обработчик запроса статистики игрока."""

    repository: Repository

    async def handle(self, query: GetPlayerStatsQuery) -> PlayerStatsResult:
        """Обрабатывает запрос статистики игрока."""
        # Проверяем валидность UUID
        try:
            player_id = UUID(str(query.player_id))
        except (ValueError, AttributeError, TypeError):
            raise ValueError("Invalid player_id")

        # Получаем игрока
        player = await self.repository.get(player_id)
        if not player:
            raise ValueError("Player not found")

        # Формируем результат
        return PlayerStatsResult(
            player_id=player.id,
            reputation=player.reputation.value,
            cases_solved=player.cases_solved,
            evidence_collected=player.evidence_collected,
            theories_submitted=player.theories_submitted,
            achievements_count=len(player.achievements),
            has_active_case=bool(player.active_case_id),
        )
