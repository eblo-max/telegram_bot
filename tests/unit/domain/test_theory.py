import pytest
from datetime import datetime
from dark_archive.domain.entities.theory import Theory


@pytest.fixture
def theory_data():
    return {
        "id": "theory123",
        "case_id": "case123",
        "description": "Теория о краже",
        "evidence_ids": [],
        "suspect_ids": [],
        "notes": [],
        "created_at": datetime.now(),
    }


@pytest.fixture
def theory(theory_data):
    return Theory(**theory_data)


def test_theory_creation(theory, theory_data):
    """Тест создания теории."""
    assert theory.id == theory_data["id"]
    assert theory.case_id == theory_data["case_id"]
    assert theory.description == theory_data["description"]
    assert theory.evidence_ids == []
    assert theory.suspect_ids == []
    assert theory.notes == []
    assert theory.created_at == theory_data["created_at"]


def test_add_evidence(theory):
    """Тест добавления улики."""
    evidence_id = "evidence123"
    theory.add_evidence(evidence_id)
    assert evidence_id in theory.evidence_ids


def test_add_suspect(theory):
    """Тест добавления подозреваемого."""
    suspect_id = "suspect123"
    theory.add_suspect(suspect_id)
    assert suspect_id in theory.suspect_ids


def test_add_note(theory):
    """Тест добавления заметки."""
    note = "Важная заметка"
    theory.add_note(note)
    assert note in theory.notes


def test_to_dict(theory, theory_data):
    """Тест преобразования в словарь."""
    data = theory.to_dict()
    assert data["id"] == theory_data["id"]
    assert data["case_id"] == theory_data["case_id"]
    assert data["description"] == theory_data["description"]
    assert data["evidence_ids"] == []
    assert data["suspect_ids"] == []
    assert data["notes"] == []
    assert data["created_at"] == theory_data["created_at"].isoformat()


def test_from_dict(theory_data):
    """Тест создания объекта из словаря."""
    data = theory_data.copy()
    data["created_at"] = data["created_at"].isoformat()
    theory = Theory.from_dict(data)

    assert theory.id == data["id"]
    assert theory.case_id == data["case_id"]
    assert theory.description == data["description"]
    assert theory.evidence_ids == []
    assert theory.suspect_ids == []
    assert theory.notes == []
    assert theory.created_at == datetime.fromisoformat(data["created_at"])


def test_create_theory():
    """Тест создания новой теории."""
    theory = Theory.create(
        case_id="case123",
        description="Новая теория",
    )

    assert theory.case_id == "case123"
    assert theory.description == "Новая теория"
    assert theory.evidence_ids == []
    assert theory.suspect_ids == []
    assert theory.notes == []
    assert isinstance(theory.created_at, datetime)


def test_remove_evidence(theory):
    """Тест удаления улики."""
    evidence_id = "evidence123"
    theory.add_evidence(evidence_id)
    theory.remove_evidence(evidence_id)
    assert evidence_id not in theory.evidence_ids


def test_remove_suspect(theory):
    """Тест удаления подозреваемого."""
    suspect_id = "suspect123"
    theory.add_suspect(suspect_id)
    theory.remove_suspect(suspect_id)
    assert suspect_id not in theory.suspect_ids


def test_clear_notes(theory):
    """Тест очистки заметок."""
    theory.add_note("Заметка 1")
    theory.add_note("Заметка 2")
    theory.clear_notes()
    assert theory.notes == []
