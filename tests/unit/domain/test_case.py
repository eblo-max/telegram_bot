import pytest
from datetime import datetime
from dark_archive.domain.entities.case import Case
from dark_archive.domain.enums import CaseStatus, CaseDifficulty


@pytest.fixture
def case_data():
    """Фикстура с данными для создания дела."""
    return {
        "id": "case123",
        "title": "Дело о краже",
        "description": "Кража из музея",
        "difficulty": CaseDifficulty.MEDIUM,
        "status": CaseStatus.OPEN,
        "created_at": datetime(2025, 3, 28, 23, 11, 43, 406197),
        "solved_at": None,
        "solution": None,
        "evidence_ids": [],
        "suspect_ids": [],
        "notes": [],
    }


@pytest.fixture
def case(case_data):
    return Case(**case_data)


def test_case_creation(case, case_data):
    """Тест создания дела."""
    assert case.id == case_data["id"]
    assert case.title == case_data["title"]
    assert case.description == case_data["description"]
    assert case.difficulty == case_data["difficulty"]
    assert case.status == case_data["status"]
    assert case.created_at == case_data["created_at"]
    assert case.solved_at == case_data["solved_at"]
    assert case.solution == case_data["solution"]
    assert case.evidence_ids == case_data["evidence_ids"]
    assert case.suspect_ids == case_data["suspect_ids"]
    assert case.notes == case_data["notes"]


def test_add_evidence(case):
    """Тест добавления улики."""
    evidence_id = "evidence123"
    case.add_evidence(evidence_id)
    assert evidence_id in case.evidence_ids


def test_add_suspect(case):
    """Тест добавления подозреваемого."""
    suspect_id = "suspect123"
    case.add_suspect(suspect_id)
    assert suspect_id in case.suspect_ids


def test_add_note(case):
    """Тест добавления заметки."""
    note = "Важная заметка"
    case.add_note(note)
    assert note in case.notes


def test_solve_case(case):
    """Тест решения дела."""
    solution = "Преступник найден"
    case.solve(solution)
    assert case.status == CaseStatus.SOLVED
    assert case.solution == solution
    assert case.solved_at is not None
    assert isinstance(case.solved_at, datetime)


def test_to_dict(case, case_data):
    """Тест преобразования в словарь."""
    data = case.to_dict()
    assert data["id"] == case_data["id"]
    assert data["title"] == case_data["title"]
    assert data["description"] == case_data["description"]
    assert data["difficulty"] == case_data["difficulty"].value
    assert data["status"] == case_data["status"].value
    assert data["created_at"] == case_data["created_at"].isoformat()
    assert data["solved_at"] is None
    assert data["solution"] is None
    assert data["evidence_ids"] == []
    assert data["suspect_ids"] == []
    assert data["notes"] == []


def test_from_dict(case_data):
    """Тест создания объекта из словаря."""
    data = case_data.copy()
    data["status"] = data["status"].value
    data["created_at"] = data["created_at"].isoformat()
    case = Case.from_dict(data)

    assert case.id == data["id"]
    assert case.title == data["title"]
    assert case.description == data["description"]
    assert case.difficulty == CaseDifficulty(data["difficulty"])
    assert case.status == CaseStatus(data["status"])
    assert case.created_at == datetime.fromisoformat(data["created_at"])
    assert case.solved_at is None
    assert case.solution is None
    assert case.evidence_ids == []
    assert case.suspect_ids == []
    assert case.notes == []


def test_create_case():
    """Тест создания нового дела."""
    case = Case.create(
        title="Новое дело",
        description="Описание дела",
        difficulty=CaseDifficulty.MEDIUM,
    )

    assert case.title == "Новое дело"
    assert case.description == "Описание дела"
    assert case.difficulty == CaseDifficulty.MEDIUM
    assert case.status == CaseStatus.NEW
    assert case.solved_at is None
    assert case.solution is None
    assert case.evidence_ids == []
    assert case.suspect_ids == []
    assert case.notes == []
    assert isinstance(case.created_at, datetime)


def test_update_status(case):
    """Тест обновления статуса."""
    case.update_status(CaseStatus.IN_PROGRESS)
    assert case.status == CaseStatus.IN_PROGRESS


def test_remove_evidence(case):
    """Тест удаления улики."""
    evidence_id = "evidence123"
    case.add_evidence(evidence_id)
    case.remove_evidence(evidence_id)
    assert evidence_id not in case.evidence_ids


def test_remove_suspect(case):
    """Тест удаления подозреваемого."""
    suspect_id = "suspect123"
    case.add_suspect(suspect_id)
    case.remove_suspect(suspect_id)
    assert suspect_id not in case.suspect_ids


def test_clear_notes(case):
    """Тест очистки заметок."""
    case.add_note("Заметка 1")
    case.add_note("Заметка 2")
    case.clear_notes()
    assert case.notes == []
