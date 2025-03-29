import pytest
from datetime import datetime
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.enums import EvidenceType


@pytest.fixture
def evidence_data():
    return {
        "id": "evidence123",
        "case_id": "case123",
        "title": "Отпечаток пальца",
        "description": "Отпечаток пальца на стене",
        "location": "Место преступления",
        "type": EvidenceType.PHYSICAL,
        "examined": False,
        "examination_notes": None,
        "relevance_score": None,
        "discovered_at": datetime.now(),
    }


@pytest.fixture
def evidence(evidence_data):
    return Evidence(**evidence_data)


def test_evidence_creation(evidence, evidence_data):
    """Тест создания улики."""
    assert evidence.id == evidence_data["id"]
    assert evidence.case_id == evidence_data["case_id"]
    assert evidence.title == evidence_data["title"]
    assert evidence.description == evidence_data["description"]
    assert evidence.location == evidence_data["location"]
    assert evidence.type == evidence_data["type"]
    assert evidence.examined == evidence_data["examined"]
    assert evidence.examination_notes == []
    assert evidence.relevance_score == evidence_data["relevance_score"]
    assert isinstance(evidence.discovered_at, datetime)


def test_examine_evidence(evidence):
    """Тест исследования улики."""
    notes = "Отпечаток принадлежит подозреваемому"
    evidence.examine(notes)
    assert evidence.examined is True
    assert len(evidence.examination_notes) == 1
    assert evidence.examination_notes[0] == notes


def test_set_relevance_score(evidence):
    """Тест установки оценки релевантности."""
    evidence.set_relevance_score(0.8)
    assert evidence.relevance_score == 0.8

    with pytest.raises(ValueError, match="Relevance score must be between 0 and 1"):
        evidence.set_relevance_score(1.5)

    assert evidence.relevance_score == 0.8


def test_add_note(evidence):
    """Тест добавления заметки."""
    note = "Важная улика"
    evidence.add_note(note)
    assert len(evidence.examination_notes) == 1
    assert evidence.examination_notes[0] == note

    with pytest.raises(ValueError, match="Note cannot be empty"):
        evidence.add_note("")


def test_mark_as_examined(evidence):
    """Тест отметки улики как исследованной."""
    evidence.mark_as_examined()
    assert evidence.examined is True


def test_to_dict(evidence, evidence_data):
    """Тест преобразования в словарь."""
    data = evidence.to_dict()
    assert data["id"] == evidence_data["id"]
    assert data["case_id"] == evidence_data["case_id"]
    assert data["title"] == evidence_data["title"]
    assert data["description"] == evidence_data["description"]
    assert data["location"] == evidence_data["location"]
    assert data["type"] == evidence_data["type"].value
    assert data["examined"] == evidence_data["examined"]
    assert data["examination_notes"] == []
    assert data["relevance_score"] == evidence_data["relevance_score"]
    assert isinstance(data["discovered_at"], str)


def test_from_dict(evidence_data):
    """Тест создания объекта из словаря."""
    data = evidence_data.copy()
    data["type"] = data["type"].value
    data["discovered_at"] = data["discovered_at"].isoformat()
    data["examination_notes"] = []
    evidence = Evidence.from_dict(data)

    assert evidence.id == data["id"]
    assert evidence.case_id == data["case_id"]
    assert evidence.title == data["title"]
    assert evidence.description == data["description"]
    assert evidence.location == data["location"]
    assert evidence.type == EvidenceType(data["type"])
    assert evidence.examined == data["examined"]
    assert evidence.examination_notes == []
    assert evidence.relevance_score == data["relevance_score"]
    assert isinstance(evidence.discovered_at, datetime)


def test_create_evidence():
    """Тест создания новой улики."""
    evidence = Evidence.create(
        case_id="case123",
        title="Новая улика",
        description="Описание улики",
        location="Место находки",
        type=EvidenceType.PHYSICAL,
    )

    assert evidence.case_id == "case123"
    assert evidence.title == "Новая улика"
    assert evidence.description == "Описание улики"
    assert evidence.location == "Место находки"
    assert evidence.type == EvidenceType.PHYSICAL
    assert evidence.examined is False
    assert evidence.examination_notes == []
    assert evidence.relevance_score is None
    assert isinstance(evidence.discovered_at, datetime)


def test_discover_evidence():
    """Тест обнаружения новой улики."""
    evidence = Evidence.discover(
        case_id="case123",
        title="Обнаруженная улика",
        description="Описание улики",
        location="Место находки",
        type=EvidenceType.PHYSICAL,
    )

    assert evidence.case_id == "case123"
    assert evidence.title == "Обнаруженная улика"
    assert evidence.description == "Описание улики"
    assert evidence.location == "Место находки"
    assert evidence.type == EvidenceType.PHYSICAL
    assert evidence.examined is False
    assert evidence.examination_notes == []
    assert evidence.relevance_score is None
    assert isinstance(evidence.discovered_at, datetime)
