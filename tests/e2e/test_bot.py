import pytest
from datetime import datetime
from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.enums import PlayerRole, CaseStatus, CaseDifficulty


@pytest.mark.asyncio
async def test_full_investigation_flow():
    """Тест полного цикла расследования."""
    # Создаем игрока
    player = Player.create(username="detective", role=PlayerRole.DETECTIVE)

    # Создаем дело
    case = Case.create(
        title="Ограбление музея",
        description="В городском музее произошло ограбление",
        difficulty=CaseDifficulty.MEDIUM,
    )

    # Назначаем дело игроку
    player.assign_case(case.id)
    assert player.active_case_id == case.id

    # Создаем подозреваемого
    suspect = Suspect.create(
        name="Иван Петров", description="Бывший сотрудник музея", case_id=case.id
    )

    # Создаем улику
    evidence = Evidence.create(
        title="Отпечатки пальцев",
        description="Отпечатки пальцев на разбитой витрине",
        case_id=case.id,
    )

    # Исследуем улику
    evidence.examine("Отпечатки совпадают с базой данных")
    assert evidence.examined

    # Допрашиваем подозреваемого
    suspect.interrogate("Подозреваемый отрицает свою причастность")
    assert suspect.interrogation_state == "interrogated"

    # Решаем дело
    case.solve("Преступление совершил Иван Петров")
    assert case.status == CaseStatus.SOLVED
    assert case.solved_at is not None
