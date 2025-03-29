import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.enums import (
    PlayerRole,
    EvidenceType,
    CaseDifficulty,
    CaseStatus,
)
from dark_archive.domain.exceptions import (
    PlayerNotFoundError,
    CaseNotFoundError,
    EvidenceNotFoundError,
    AccessDeniedError,
    EvidenceAlreadyExaminedError,
)
from dark_archive.application.use_cases.examine_evidence import (
    ExamineEvidenceUseCase,
    ExamineEvidenceCommand,
    ExamineEvidenceRequest,
    ExamineEvidenceResponse,
)


@pytest.fixture
def player():
    return Player(
        id="player123",
        username="detective",
        role=PlayerRole.DETECTIVE,
        active_case_id="case123",
        solved_cases=[],
        created_at=datetime.now(),
        last_active=datetime.now(),
    )


@pytest.fixture
def case():
    return Case(
        id="case123",
        title="Дело о краже",
        description="Кража из музея",
        difficulty=CaseDifficulty.MEDIUM,
        status=CaseStatus.OPEN,
        created_at=datetime.now(),
        solved_at=None,
        solution=None,
        evidence_ids=["evidence123"],
        suspect_ids=[],
        notes=[],
    )


@pytest.fixture
def evidence():
    return Evidence(
        id="evidence123",
        case_id="case123",
        title="Отпечаток пальца",
        description="Отпечаток пальца на стене",
        location="Место преступления",
        type=EvidenceType.PHYSICAL,
        examined=False,
        examination_notes=[],
        relevance_score=None,
        discovered_at=datetime.now(),
    )


@pytest.fixture
def player_repository():
    repository = AsyncMock()
    repository.get_by_id = AsyncMock()
    return repository


@pytest.fixture
def case_repository():
    repository = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.save = AsyncMock()
    return repository


@pytest.fixture
def use_case(player_repository, case_repository):
    return ExamineEvidenceUseCase(player_repository, case_repository)


@pytest.mark.asyncio
async def test_execute_success(use_case, player, case, evidence):
    """Тест успешного выполнения use case."""
    # Настраиваем моки
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    case.get_evidence = MagicMock(return_value=evidence)

    # Создаем команду
    command = ExamineEvidenceCommand(
        player_id="player123",
        case_id="case123",
        evidence_id="evidence123",
        notes="Отпечаток принадлежит подозреваемому",
    )

    # Выполняем use case
    result = await use_case.execute(command)

    # Проверяем результаты
    assert isinstance(result, ExamineEvidenceResponse)
    assert result.evidence == evidence
    assert evidence.examined is True
    assert len(evidence.examination_notes) == 1
    assert evidence.examination_notes[0] == "Отпечаток принадлежит подозреваемому"
    use_case.case_repository.save.assert_called_once_with(case)


@pytest.mark.asyncio
async def test_execute_player_not_found(use_case):
    """Тест ошибки при отсутствии игрока."""
    use_case.player_repository.get_by_id.return_value = None

    command = ExamineEvidenceCommand(
        player_id="nonexistent",
        case_id="case123",
        evidence_id="evidence123",
    )

    with pytest.raises(PlayerNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_case_not_found(use_case, player):
    """Тест ошибки при отсутствии дела."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = None

    command = ExamineEvidenceCommand(
        player_id="player123",
        case_id="nonexistent",
        evidence_id="evidence123",
    )

    with pytest.raises(CaseNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_evidence_not_found(use_case, player, case):
    """Тест ошибки при отсутствии улики."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    case.get_evidence = MagicMock(return_value=None)

    command = ExamineEvidenceCommand(
        player_id="player123",
        case_id="case123",
        evidence_id="nonexistent",
    )

    with pytest.raises(EvidenceNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_access_denied(use_case, player, case):
    """Тест ошибки при отсутствии доступа к делу."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    player.has_access_to_case = MagicMock(return_value=False)

    command = ExamineEvidenceCommand(
        player_id="player123",
        case_id="case123",
        evidence_id="evidence123",
    )

    with pytest.raises(AccessDeniedError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_evidence_already_examined(use_case, player, case, evidence):
    """Тест ошибки при попытке повторного исследования улики."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    case.get_evidence = MagicMock(return_value=evidence)
    evidence.examined = True

    command = ExamineEvidenceCommand(
        player_id="player123",
        case_id="case123",
        evidence_id="evidence123",
    )

    with pytest.raises(EvidenceAlreadyExaminedError):
        await use_case.execute(command)


def test_execute_sync_success(use_case, evidence):
    """Тест успешного выполнения синхронного метода."""
    request = ExamineEvidenceRequest(
        evidence=evidence,
        notes="Отпечаток принадлежит подозреваемому",
    )

    response = use_case.execute_sync(request)

    assert isinstance(response, ExamineEvidenceResponse)
    assert response.evidence == evidence
    assert evidence.examined is True
    assert len(evidence.examination_notes) == 1
    assert evidence.examination_notes[0] == "Отпечаток принадлежит подозреваемому"


def test_execute_sync_evidence_not_found(use_case):
    """Тест ошибки при отсутствии улики в синхронном методе."""
    request = ExamineEvidenceRequest(
        evidence=None,
        notes="Заметка",
    )

    with pytest.raises(EvidenceNotFoundError):
        use_case.execute_sync(request)


def test_execute_sync_evidence_already_examined(use_case, evidence):
    """Тест ошибки при попытке повторного исследования улики в синхронном методе."""
    evidence.examined = True
    request = ExamineEvidenceRequest(
        evidence=evidence,
        notes="Заметка",
    )

    with pytest.raises(EvidenceAlreadyExaminedError):
        use_case.execute_sync(request)
