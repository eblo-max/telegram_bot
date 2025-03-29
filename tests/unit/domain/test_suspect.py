import pytest
from datetime import datetime, timedelta
from dark_archive.domain.entities.suspect import Suspect, SuspectStatus


@pytest.fixture
def suspect_data():
    return {
        "id": "suspect123",
        "case_id": "case123",
        "name": "Иван Иванов",
        "description": "Подозреваемый в краже",
        "interrogation_state": "not_interrogated",
        "interrogation_cooldown_until": None,
        "interrogation_notes": [],
        "motives": [],
        "alibi": "Был дома",
    }


@pytest.fixture
def suspect(suspect_data):
    return Suspect(**suspect_data)


def test_suspect_creation(suspect, suspect_data):
    """Тест создания подозреваемого."""
    assert suspect.id == suspect_data["id"]
    assert suspect.case_id == suspect_data["case_id"]
    assert suspect.name == suspect_data["name"]
    assert suspect.description == suspect_data["description"]
    assert suspect.interrogation_state == suspect_data["interrogation_state"]
    assert (
        suspect.interrogation_cooldown_until
        == suspect_data["interrogation_cooldown_until"]
    )
    assert suspect.interrogation_notes == suspect_data["interrogation_notes"]
    assert suspect.motives == suspect_data["motives"]
    assert suspect.alibi == suspect_data["alibi"]
    assert suspect.status == SuspectStatus.UNKNOWN
    assert suspect.risk_level == 0
    assert suspect.evidence_ids == []
    assert suspect.notes == ""


def test_can_be_interrogated(suspect):
    """Тест проверки возможности допроса."""
    assert suspect.can_be_interrogated() is True

    suspect.set_cooldown(hours=1)
    assert suspect.can_be_interrogated() is False


def test_add_interrogation_note(suspect):
    """Тест добавления заметки к допросу."""
    note = "Подозреваемый нервничал во время допроса"
    suspect.add_interrogation_note(note)
    assert len(suspect.interrogation_notes) == 1
    assert suspect.interrogation_notes[0] == note


def test_add_motive(suspect):
    """Тест добавления мотива."""
    motive = "Финансовая выгода"
    suspect.add_motive(motive)
    assert len(suspect.motives) == 1
    assert suspect.motives[0] == motive


def test_set_cooldown(suspect):
    """Тест установки времени до следующего допроса."""
    suspect.set_cooldown(hours=2)
    assert suspect.interrogation_cooldown_until is not None
    assert isinstance(suspect.interrogation_cooldown_until, datetime)
    assert suspect.interrogation_cooldown_until > datetime.now()


def test_to_dict(suspect, suspect_data):
    """Тест преобразования в словарь."""
    data = suspect.to_dict()
    assert data["id"] == suspect_data["id"]
    assert data["case_id"] == suspect_data["case_id"]
    assert data["name"] == suspect_data["name"]
    assert data["description"] == suspect_data["description"]
    assert data["interrogation_state"] == suspect_data["interrogation_state"]
    assert data["interrogation_cooldown_until"] is None
    assert data["interrogation_notes"] == suspect_data["interrogation_notes"]
    assert data["motives"] == suspect_data["motives"]
    assert data["alibi"] == suspect_data["alibi"]


def test_from_dict(suspect_data):
    """Тест создания объекта из словаря."""
    data = suspect_data.copy()
    suspect = Suspect.from_dict(data)

    assert suspect.id == data["id"]
    assert suspect.case_id == data["case_id"]
    assert suspect.name == data["name"]
    assert suspect.description == data["description"]
    assert suspect.interrogation_state == data["interrogation_state"]
    assert suspect.interrogation_cooldown_until == data["interrogation_cooldown_until"]
    assert suspect.interrogation_notes == data["interrogation_notes"]
    assert suspect.motives == data["motives"]
    assert suspect.alibi == data["alibi"]


def test_create_suspect():
    """Тест создания нового подозреваемого."""
    suspect = Suspect.create(
        case_id="case123",
        name="Новый подозреваемый",
        description="Описание подозреваемого",
        interrogation_state="not_interrogated",
        interrogation_cooldown_until=None,
        interrogation_notes=[],
        motives=[],
        alibi="",
    )

    assert suspect.name == "Новый подозреваемый"
    assert suspect.description == "Описание подозреваемого"
    assert suspect.case_id == "case123"
    assert suspect.interrogation_state == "not_interrogated"
    assert suspect.interrogation_cooldown_until is None
    assert suspect.interrogation_notes == []
    assert suspect.motives == []
    assert suspect.alibi == ""
    assert suspect.status == SuspectStatus.UNKNOWN
    assert suspect.risk_level == 0
    assert suspect.evidence_ids == []
    assert suspect.notes == ""


def test_update_status(suspect):
    """Тест обновления статуса."""
    suspect.update_status(SuspectStatus.ARRESTED)
    assert suspect.status == SuspectStatus.ARRESTED


def test_add_evidence(suspect):
    """Тест добавления улики."""
    evidence_id = "evidence123"
    suspect.add_evidence(evidence_id)
    assert evidence_id in suspect.evidence_ids


def test_add_note(suspect):
    """Тест добавления заметки."""
    note1 = "Первая заметка"
    note2 = "Вторая заметка"

    suspect.add_note(note1)
    assert suspect.notes == note1

    suspect.add_note(note2)
    assert suspect.notes == f"{note1}\n{note2}"


def test_set_alibi(suspect):
    """Тест установки алиби."""
    alibi = "Был в кинотеатре"
    suspect.set_alibi(alibi)
    assert suspect.alibi == alibi


def test_set_motive(suspect):
    """Тест установки мотива."""
    motive = "Месть"
    suspect.set_motive(motive)
    assert suspect.motive == motive
