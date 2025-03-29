import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.entities.theory import Theory
from dark_archive.domain.enums import (
    PlayerRole,
    CaseStatus,
    EvidenceType,
    SuspectStatus,
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
        status=CaseStatus.OPEN,
        created_at=datetime.now(),
        solved_at=None,
        solution=None,
        evidence_ids=["evidence123"],
        suspect_ids=["suspect123"],
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
def theory():
    return Theory(
        id="theory123",
        case_id="case123",
        description="Теория о краже",
        evidence_ids=["evidence123"],
        suspect_ids=["suspect123"],
        notes=[],
        created_at=datetime.now(),
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
def evidence_repository():
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
def theory_repository():
    repository = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.save = AsyncMock()
    return repository
