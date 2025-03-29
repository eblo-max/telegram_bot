# Created by setup script

from dataclasses import dataclass
from typing import List

from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.theory import Theory
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.exceptions import (
    PlayerNotFoundError,
    CaseNotFoundError,
    EvidenceNotFoundError,
    AccessDeniedError,
    InvalidTheoryError,
)


@dataclass
class BuildTheoryCommand:
    """Команда для построения теории."""

    player_id: str
    case_id: str
    evidence_ids: List[str]
    description: str


class BuildTheoryUseCase:
    """Use case для построения теории на основе улик."""

    def __init__(self, player_repository, case_repository):
        self.player_repository = player_repository
        self.case_repository = case_repository

    async def execute(self, command: BuildTheoryCommand) -> Theory:
        """
        Выполняет построение теории.

        Args:
            command: Команда с данными для построения теории

        Returns:
            Theory: Построенная теория

        Raises:
            PlayerNotFoundError: Если игрок не найден
            CaseNotFoundError: Если дело не найдено
            EvidenceNotFoundError: Если улика не найдена
            InvalidTheoryError: Если теория невалидна
        """
        # Получаем игрока
        player = await self.player_repository.get_by_id(command.player_id)
        if not player:
            raise PlayerNotFoundError(f"Player with id {command.player_id} not found")

        # Получаем дело
        case = await self.case_repository.get_by_id(command.case_id)
        if not case:
            raise CaseNotFoundError(f"Case with id {command.case_id} not found")

        # Проверяем, что игрок имеет доступ к делу
        if not player.has_access_to_case(case):
            raise AccessDeniedError("Player does not have access to this case")

        # Получаем улики
        evidence_list = []
        for evidence_id in command.evidence_ids:
            evidence = case.get_evidence(evidence_id)
            if not evidence:
                raise EvidenceNotFoundError(f"Evidence with id {evidence_id} not found")
            evidence_list.append(evidence)

        # Создаем теорию
        theory = Theory(
            player_id=command.player_id,
            case_id=command.case_id,
            evidence_ids=command.evidence_ids,
            description=command.description,
        )

        # Валидируем теорию
        if not theory.is_valid():
            raise InvalidTheoryError("Theory is invalid")

        # Добавляем теорию к делу
        case.add_theory(theory)

        # Сохраняем изменения
        await self.case_repository.save(case)

        return theory
