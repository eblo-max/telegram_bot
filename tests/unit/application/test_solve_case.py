import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.enums import PlayerRole, CaseStatus, CaseDifficulty
from dark_archive.domain.exceptions import (
    PlayerNotFoundError,
    CaseNotFoundError,
    AccessDeniedError,
    CaseAlreadySolvedError,
    InvalidSolutionError,
)
from dark_archive.application.use_cases.solve_case import (
    SolveCaseUseCase,
    SolveCaseCommand,
    SolveCaseRequest,
    SolveCaseResponse,
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
        suspect_ids=[],
        notes=[],
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
    return SolveCaseUseCase(player_repository, case_repository)


@pytest.mark.asyncio
async def test_execute_success(use_case, player, case):
    """Тест успешного выполнения use case."""
    # Настраиваем моки
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case

    # Создаем команду
    command = SolveCaseCommand(
        player_id="player123",
        case_id="case123",
        solution="Преступление совершил дворецкий",
    )

    # Выполняем use case
    result = await use_case.execute(command)

    # Проверяем результаты
    assert isinstance(result, SolveCaseResponse)
    assert result.case == case
    assert case.solution == "Преступление совершил дворецкий"
    assert case.solved is True
    use_case.case_repository.save.assert_called_once_with(case)
    use_case.player_repository.save.assert_called_once_with(player)


@pytest.mark.asyncio
async def test_execute_player_not_found(use_case):
    """Тест ошибки при отсутствии игрока."""
    use_case.player_repository.get_by_id.return_value = None

    command = SolveCaseCommand(
        player_id="nonexistent",
        case_id="case123",
        solution="Решение",
    )

    with pytest.raises(PlayerNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_case_not_found(use_case, player):
    """Тест ошибки при отсутствии дела."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = None

    command = SolveCaseCommand(
        player_id="player123",
        case_id="nonexistent",
        solution="Решение",
    )

    with pytest.raises(CaseNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_access_denied(use_case, player, case):
    """Тест ошибки при отсутствии доступа к делу."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    player.has_access_to_case = MagicMock(return_value=False)

    command = SolveCaseCommand(
        player_id="player123",
        case_id="case123",
        solution="Решение",
    )

    with pytest.raises(AccessDeniedError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_case_already_solved(use_case, player, case):
    """Тест ошибки при попытке решения уже решенного дела."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case
    case.status = CaseStatus.SOLVED
    case.solution = "Уже решено"
    case.solved_at = datetime.now()

    command = SolveCaseCommand(
        player_id="player123",
        case_id="case123",
        solution="Новое решение",
    )

    with pytest.raises(CaseAlreadySolvedError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_execute_invalid_solution(use_case, player, case):
    """Тест ошибки при неверном решении."""
    use_case.player_repository.get_by_id.return_value = player
    use_case.case_repository.get_by_id.return_value = case

    command = SolveCaseCommand(
        player_id="player123",
        case_id="case123",
        solution="",  # Пустое решение
    )

    with pytest.raises(InvalidSolutionError):
        await use_case.execute(command)


def test_execute_sync_success(use_case, case):
    """Тест успешного выполнения синхронного метода."""
    request = SolveCaseRequest(
        case=case,
        solution="Преступление совершил дворецкий",
    )

    response = use_case.execute_sync(request)

    assert isinstance(response, SolveCaseResponse)
    assert response.case == case
    assert case.solution == "Преступление совершил дворецкий"
    assert case.solved is True


def test_execute_sync_case_not_found(use_case):
    """Тест ошибки при отсутствии дела в синхронном методе."""
    request = SolveCaseRequest(
        case=None,
        solution="Решение",
    )

    with pytest.raises(CaseNotFoundError):
        use_case.execute_sync(request)


def test_execute_sync_case_already_solved(use_case, case):
    """Тест ошибки при попытке решения уже решенного дела в синхронном методе."""
    case.status = CaseStatus.SOLVED
    case.solution = "Уже решено"
    case.solved_at = datetime.now()

    request = SolveCaseRequest(
        case=case,
        solution="Новое решение",
    )

    with pytest.raises(CaseAlreadySolvedError):
        use_case.execute_sync(request)


def test_execute_sync_invalid_solution(use_case, case):
    """Тест ошибки при неверном решении в синхронном методе."""
    request = SolveCaseRequest(
        case=case,
        solution="",  # Пустое решение
    )

    with pytest.raises(InvalidSolutionError):
        use_case.execute_sync(request)
