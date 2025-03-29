import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass

from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.suspect import Suspect, SuspectStatus
from dark_archive.domain.enums import PlayerRole, CaseDifficulty, CaseStatus
from dark_archive.domain.exceptions import (
    PlayerNotFoundError,
    CaseNotFoundError,
    SuspectNotFoundError,
    AccessDeniedError,
    SuspectInterrogationError,
)
from dark_archive.application.use_cases.interrogate_suspect import (
    InterrogateSuspectUseCase,
    InterrogateSuspectCommand,
    InterrogateSuspectRequest,
    InterrogateSuspectResponse,
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
        evidence_ids=[],
        suspect_ids=["suspect123"],
        notes=[],
    )


@pytest.fixture
def suspect():
    return Suspect(
        id="suspect123",
        case_id="case123",
        name="Иван Иванов",
        description="Подозреваемый в краже",
        interrogation_state="not_interrogated",
        interrogation_cooldown_until=None,
        interrogation_notes=[],
        motives=[],
        alibi="Был дома",
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
def suspect_repository():
    repository = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.save = AsyncMock()
    return repository


@pytest.fixture
def use_case(player_repository, case_repository, suspect_repository):
    return InterrogateSuspectUseCase(
        player_repository=player_repository,
        case_repository=case_repository,
        suspect_repository=suspect_repository,
    )


@pytest.mark.asyncio
async def test_execute_success(use_case, player, case, suspect):
    """Тест успешного выполнения use case."""
    # Настраиваем моки
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    use_case.suspect_repository.get_by_id.return_value = suspect

    # Создаем команду
    command = InterrogateSuspectCommand(
        player_id="player123",
        case_id="case123",
        suspect_id="suspect123",
        notes="Подозреваемый отрицает свою причастность",
    )

    # Выполняем use case
    result = await use_case.execute(command)

    # Проверяем результаты
    assert isinstance(result, InterrogateSuspectResponse)
    assert result.suspect == suspect
    assert len(suspect.interrogation_notes) == 1
    assert suspect.interrogation_notes[0] == "Подозреваемый отрицает свою причастность"
    use_case.suspect_repository.save.assert_called_once_with(suspect)


@pytest.mark.asyncio
async def test_execute_player_not_found(use_case):
    """Тест ошибки при отсутствии игрока."""
    use_case.player_repository.get_by_id.return_value = None

    command = InterrogateSuspectCommand(
        player_id="nonexistent",
        case_id="case123",
        suspect_id="suspect123",
    )

    with pytest.raises(PlayerNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_case_not_found(use_case, player):
    """Тест ошибки при отсутствии дела."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = None

    command = InterrogateSuspectCommand(
        player_id="player123",
        case_id="nonexistent",
        suspect_id="suspect123",
    )

    with pytest.raises(CaseNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_suspect_not_found(use_case, player, case):
    """Тест ошибки при отсутствии подозреваемого."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    use_case.suspect_repository.get_by_id.return_value = None

    command = InterrogateSuspectCommand(
        player_id="player123",
        case_id="case123",
        suspect_id="nonexistent",
    )

    with pytest.raises(SuspectNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_access_denied(use_case, player, case):
    """Тест ошибки при отсутствии доступа к делу."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    player.has_access_to_case = MagicMock(return_value=False)

    command = InterrogateSuspectCommand(
        player_id="player123",
        case_id="case123",
        suspect_id="suspect123",
    )

    with pytest.raises(AccessDeniedError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_suspect_in_cooldown(use_case, player, case, suspect):
    """Тест ошибки при попытке допроса подозреваемого в период ожидания."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    use_case.suspect_repository.get_by_id.return_value = suspect
    suspect.interrogation_cooldown_until = datetime.now() + timedelta(hours=1)

    command = InterrogateSuspectCommand(
        player_id="player123",
        case_id="case123",
        suspect_id="suspect123",
    )

    with pytest.raises(SuspectInterrogationError):
        await use_case.execute(command)


def test_execute_sync_success(use_case, suspect):
    """Тест успешного выполнения синхронного метода."""
    request = InterrogateSuspectRequest(
        suspect=suspect,
        notes="Подозреваемый отрицает свою причастность",
    )

    response = use_case.execute_sync(request)

    assert isinstance(response, InterrogateSuspectResponse)
    assert response.suspect == suspect
    assert len(suspect.interrogation_notes) == 1
    assert suspect.interrogation_notes[0] == "Подозреваемый отрицает свою причастность"


def test_execute_sync_suspect_not_found(use_case):
    """Тест ошибки при отсутствии подозреваемого в синхронном методе."""
    request = InterrogateSuspectRequest(
        suspect=None,
        notes="Заметка",
    )

    with pytest.raises(SuspectNotFoundError):
        use_case.execute_sync(request)


def test_execute_sync_suspect_in_cooldown(use_case, suspect):
    """Тест ошибки при попытке допроса подозреваемого в период ожидания в синхронном методе."""
    suspect.interrogation_cooldown_until = datetime.now() + timedelta(hours=1)
    request = InterrogateSuspectRequest(
        suspect=suspect,
        notes="Заметка",
    )

    with pytest.raises(SuspectInterrogationError):
        use_case.execute_sync(request)
