import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.application.use_cases.examine_evidence import (
    ExamineEvidenceUseCase,
    ExamineEvidenceCommand,
)
from dark_archive.application.use_cases.interrogate_suspect import (
    InterrogateSuspectUseCase,
    InterrogateSuspectCommand,
)
from dark_archive.domain.enums import PlayerRole, CaseStatus, CaseDifficulty


@pytest.fixture
def player_repository():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def case_repository():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def evidence_repository():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def suspect_repository():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.save = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_examine_evidence_flow(
    player_repository, case_repository, evidence_repository
):
    """Тест процесса исследования улики."""
    # Создаем use case
    examine_evidence_use_case = ExamineEvidenceUseCase(
        player_repository=player_repository,
        case_repository=case_repository,
        evidence_repository=evidence_repository,
    )

    # Создаем тестовые данные
    player = Player.create(username="detective", role=PlayerRole.DETECTIVE)
    case = Case.create(
        title="Ограбление",
        description="Ограбление банка",
        difficulty=CaseDifficulty.MEDIUM,
    )
    evidence = Evidence.create(
        title="Отпечатки", description="Отпечатки на сейфе", case_id=case.id
    )

    # Назначаем дело игроку
    player.assign_case(case.id)

    # Настраиваем моки
    player_repository.get_by_id.return_value = player
    case_repository.get_by_id.return_value = case
    evidence_repository.get_by_id.return_value = evidence

    # Выполняем use case
    result = await examine_evidence_use_case.execute(
        command=ExamineEvidenceCommand(
            player_id=player.id,
            case_id=case.id,
            evidence_id=evidence.id,
            notes="Отпечатки принадлежат подозреваемому",
        )
    )

    # Проверяем результат
    assert result.evidence.examined
    assert "Отпечатки принадлежат подозреваемому" in result.evidence.examination_notes
    evidence_repository.save.assert_called_once_with(evidence)


@pytest.mark.asyncio
async def test_interrogate_suspect_flow(
    player_repository, case_repository, suspect_repository
):
    """Тест процесса допроса подозреваемого."""
    # Создаем use case
    interrogate_suspect_use_case = InterrogateSuspectUseCase(
        player_repository=player_repository,
        case_repository=case_repository,
        suspect_repository=suspect_repository,
    )

    # Создаем тестовые данные
    player = Player.create(username="detective", role=PlayerRole.DETECTIVE)
    case = Case.create(
        title="Ограбление",
        description="Ограбление банка",
        difficulty=CaseDifficulty.MEDIUM,
    )
    suspect = Suspect.create(
        name="Подозреваемый", description="Главный подозреваемый", case_id=case.id
    )

    # Назначаем дело игроку
    player.assign_case(case.id)

    # Настраиваем моки
    player_repository.get_by_id.return_value = player
    case_repository.get_by_id.return_value = case
    suspect_repository.get_by_id.return_value = suspect

    # Выполняем use case
    result = await interrogate_suspect_use_case.execute(
        command=InterrogateSuspectCommand(
            player_id=player.id,
            case_id=case.id,
            suspect_id=suspect.id,
            notes="Подозреваемый отрицает вину",
        )
    )

    # Проверяем результат
    assert result.suspect.interrogation_state == "interrogated"
    assert "Подозреваемый отрицает вину" in result.suspect.interrogation_notes
    suspect_repository.save.assert_called_once_with(suspect)
