import pytest
from datetime import datetime
from dark_archive.domain.entities.player import Player
from dark_archive.domain.enums import PlayerRole


@pytest.fixture
def player_data():
    return {
        "id": "player123",
        "username": "detective",
        "role": PlayerRole.DETECTIVE,
        "active_case_id": None,
        "solved_cases": [],
        "created_at": datetime.now(),
        "last_active": datetime.now(),
    }


@pytest.fixture
def player(player_data):
    return Player(**player_data)


def test_player_creation(player, player_data):
    """Тест создания игрока."""
    assert player.id == player_data["id"]
    assert player.username == player_data["username"]
    assert player.role == player_data["role"]
    assert player.active_case_id is None
    assert player.solved_cases == []
    assert player.created_at == player_data["created_at"]
    assert player.last_active == player_data["last_active"]


def test_assign_case(player):
    """Тест назначения дела."""
    case_id = "case123"
    player.assign_case(case_id)
    assert player.active_case_id == case_id


def test_complete_case(player):
    """Тест завершения дела."""
    case_id = "case123"
    player.assign_case(case_id)
    player.complete_case(case_id)
    assert player.active_case_id is None
    assert case_id in player.solved_cases


def test_update_last_active(player):
    """Тест обновления времени последней активности."""
    old_time = player.last_active
    player.update_last_active()
    assert player.last_active > old_time


def test_to_dict(player, player_data):
    """Тест преобразования в словарь."""
    data = player.to_dict()
    assert data["id"] == player_data["id"]
    assert data["username"] == player_data["username"]
    assert data["role"] == player_data["role"].value
    assert data["active_case_id"] is None
    assert data["solved_cases"] == []
    assert data["created_at"] == player_data["created_at"].isoformat()
    assert data["last_active"] == player_data["last_active"].isoformat()


def test_from_dict(player_data):
    """Тест создания объекта из словаря."""
    data = player_data.copy()
    data["role"] = data["role"].value
    data["created_at"] = data["created_at"].isoformat()
    data["last_active"] = data["last_active"].isoformat()
    player = Player.from_dict(data)

    assert player.id == data["id"]
    assert player.username == data["username"]
    assert player.role == PlayerRole(data["role"])
    assert player.active_case_id is None
    assert player.solved_cases == []
    assert player.created_at == datetime.fromisoformat(data["created_at"])
    assert player.last_active == datetime.fromisoformat(data["last_active"])


def test_create_player():
    """Тест создания нового игрока."""
    player = Player.create(
        username="new_detective",
        role=PlayerRole.DETECTIVE,
    )

    assert player.username == "new_detective"
    assert player.role == PlayerRole.DETECTIVE
    assert player.active_case_id is None
    assert player.solved_cases == []
    assert isinstance(player.created_at, datetime)
    assert isinstance(player.last_active, datetime)


def test_has_active_case(player):
    """Тест проверки наличия активного дела."""
    assert player.has_active_case() is False

    player.assign_case("case123")
    assert player.has_active_case() is True


def test_has_solved_case(player):
    """Тест проверки наличия решенного дела."""
    assert player.has_solved_case("case123") is False

    player.complete_case("case123")
    assert player.has_solved_case("case123") is True


def test_change_role(player):
    """Тест изменения роли."""
    player.change_role(PlayerRole.ADMIN)
    assert player.role == PlayerRole.ADMIN


def test_clear_active_case(player):
    """Тест очистки активного дела."""
    player.assign_case("case123")
    player.clear_active_case()
    assert player.active_case_id is None
