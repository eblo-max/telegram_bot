"""Тесты сериализации и десериализации сущностей."""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from dark_archive.domain.enums import (
    CaseDifficulty,
    CaseStatus,
    EvidenceType,
    PlayerRole,
    SuspectStatus,
)
from dark_archive.domain.entities.base import BaseEntity
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.entities.player import Player


def test_case_serialization():
    """Тест сериализации и десериализации дела."""
    # Создаем тестовое дело
    case = Case.create(
        title="Ограбление музея",
        description="В городском музее произошло ограбление",
        difficulty=CaseDifficulty.MEDIUM,
    )

    # Сериализуем дело
    case_dict = case.to_dict()

    # Проверяем структуру словаря
    assert "id" in case_dict
    assert "title" in case_dict
    assert "description" in case_dict
    assert "difficulty" in case_dict
    assert "status" in case_dict
    assert "created_at" in case_dict
    assert "updated_at" in case_dict
    assert "evidence" in case_dict
    assert "locations" in case_dict
    assert "suspects" in case_dict
    assert "detective_notes" in case_dict

    # Создаем новое дело из словаря
    new_case = Case.from_dict(case_dict)

    # Проверяем, что все поля совпадают
    assert str(new_case.id) == case_dict["id"]
    assert new_case.title == case.title
    assert new_case.description == case.description
    assert new_case.difficulty == case.difficulty
    assert new_case.status == case.status
    assert new_case.evidence == case.evidence
    assert new_case.locations == case.locations
    assert new_case.suspects == case.suspects
    assert new_case.detective_notes == case.detective_notes


def test_evidence_serialization():
    """Тест сериализации и десериализации улики."""
    case_id = uuid4()
    # Создаем тестовую улику
    evidence = Evidence.create(
        case_id=case_id,
        title="Отпечатки пальцев",
        description="Отпечатки пальцев на разбитой витрине",
        location="Главный зал музея",
        type=EvidenceType.PHYSICAL,
    )

    # Сериализуем улику
    evidence_dict = evidence.to_dict()

    # Проверяем структуру словаря
    assert "id" in evidence_dict
    assert "title" in evidence_dict
    assert "description" in evidence_dict
    assert "case_id" in evidence_dict
    assert "location" in evidence_dict
    assert "type" in evidence_dict
    assert "examined" in evidence_dict
    assert "examination_notes" in evidence_dict
    assert "created_at" in evidence_dict
    assert "updated_at" in evidence_dict

    # Создаем новую улику из словаря
    new_evidence = Evidence.from_dict(evidence_dict)

    # Проверяем, что все поля совпадают
    assert str(new_evidence.id) == evidence_dict["id"]
    assert new_evidence.title == evidence.title
    assert new_evidence.description == evidence.description
    assert str(new_evidence.case_id) == evidence_dict["case_id"]
    assert new_evidence.location == evidence.location
    assert new_evidence.type == evidence.type
    assert new_evidence.examined == evidence.examined
    assert new_evidence.examination_notes == evidence.examination_notes


def test_location_serialization():
    """Тест сериализации и десериализации локации."""
    # Создаем тестовую локацию
    location = Location(
        name="Главный зал музея",
        description="Центральный выставочный зал с витринами",
        case_id=uuid4(),
    )

    # Сериализуем локацию
    location_dict = location.to_dict()

    # Проверяем структуру словаря
    assert "id" in location_dict
    assert "name" in location_dict
    assert "description" in location_dict
    assert "case_id" in location_dict
    assert "visited" in location_dict
    assert "visit_notes" in location_dict
    assert "created_at" in location_dict
    assert "updated_at" in location_dict

    # Создаем новую локацию из словаря
    new_location = Location.from_dict(location_dict)

    # Проверяем, что все поля совпадают
    assert str(new_location.id) == location_dict["id"]
    assert new_location.name == location.name
    assert new_location.description == location.description
    assert str(new_location.case_id) == location_dict["case_id"]
    assert new_location.visited == location.visited
    assert new_location.visit_notes == location.visit_notes


def test_suspect_serialization():
    """Тест сериализации и десериализации подозреваемого."""
    # Создаем тестового подозреваемого
    suspect = Suspect(
        name="Иван Петров",
        description="Бывший сотрудник музея",
        case_id=uuid4(),
    )

    # Сериализуем подозреваемого
    suspect_dict = suspect.to_dict()

    # Проверяем структуру словаря
    assert "id" in suspect_dict
    assert "name" in suspect_dict
    assert "description" in suspect_dict
    assert "case_id" in suspect_dict
    assert "status" in suspect_dict
    assert "interrogation_state" in suspect_dict
    assert "interrogation_notes" in suspect_dict
    assert "created_at" in suspect_dict
    assert "updated_at" in suspect_dict

    # Создаем нового подозреваемого из словаря
    new_suspect = Suspect.from_dict(suspect_dict)

    # Проверяем, что все поля совпадают
    assert str(new_suspect.id) == suspect_dict["id"]
    assert new_suspect.name == suspect.name
    assert new_suspect.description == suspect.description
    assert str(new_suspect.case_id) == suspect_dict["case_id"]
    assert new_suspect.status == suspect.status
    assert new_suspect.interrogation_state == suspect.interrogation_state
    assert new_suspect.interrogation_notes == suspect.interrogation_notes


def test_player_serialization():
    """Тест сериализации и десериализации игрока."""
    # Создаем тестового игрока
    player = Player(
        username="detective_user",
        role=PlayerRole.DETECTIVE,
        telegram_id=12345,
    )

    # Сериализуем игрока
    player_dict = player.to_dict()

    # Проверяем структуру словаря
    assert "id" in player_dict
    assert "username" in player_dict
    assert "role" in player_dict
    assert "telegram_id" in player_dict
    assert "active_case_id" in player_dict
    assert "solved_cases" in player_dict
    assert "last_active" in player_dict

    # Создаем нового игрока из словаря
    new_player = Player.from_dict(player_dict)

    # Проверяем, что все поля совпадают
    assert str(new_player.id) == player_dict["id"]
    assert new_player.username == player.username
    assert new_player.role == player.role
    assert new_player.telegram_id == player.telegram_id
    assert new_player.active_case_id == player.active_case_id
    assert new_player.solved_cases == player.solved_cases
    assert new_player.last_active == player.last_active
