"""Тесты для доменной модели."""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from dark_archive.domain.entities.case import Case, CaseDifficulty, CaseStatus
from dark_archive.domain.entities.evidence import Evidence, EvidenceType
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect, SuspectStatus
from dark_archive.domain.exceptions import SuspectInterrogationError


@pytest.fixture
def test_case():
    """Фикстура для тестового дела."""
    return Case.create(
        title="Ограбление музея",
        description="В городском музее произошло ограбление",
        difficulty=CaseDifficulty.MEDIUM,
    )


@pytest.fixture
def test_location():
    """Фикстура для тестовой локации."""
    return Location.create(
        name="Главный зал музея",
        description="Центральный выставочный зал с витринами",
        case_id=uuid4(),
    )


@pytest.fixture
def test_evidence():
    """Фикстура для тестовой улики."""
    return Evidence.create(
        title="Отпечатки пальцев",
        description="Отпечатки пальцев на разбитой витрине",
        case_id=uuid4(),
        location="Главный зал музея",
        type=EvidenceType.PHYSICAL,
    )


@pytest.fixture
def test_suspect():
    """Фикстура для тестового подозреваемого."""
    return Suspect.create(
        name="Иван Петров",
        description="Бывший сотрудник музея",
        case_id=str(uuid4()),
    )


def test_case_creation(test_case):
    """Тест создания дела."""
    assert isinstance(test_case.id, UUID)
    assert test_case.title == "Ограбление музея"
    assert test_case.description == "В городском музее произошло ограбление"
    assert test_case.difficulty == CaseDifficulty.MEDIUM
    assert test_case.status == CaseStatus.NEW
    assert isinstance(test_case.created_at, datetime)
    assert isinstance(test_case.updated_at, datetime)
    assert test_case.evidence == []
    assert test_case.locations == []


def test_location_creation(test_location):
    """Тест создания локации."""
    assert isinstance(test_location.id, UUID)
    assert test_location.name == "Главный зал музея"
    assert test_location.description == "Центральный выставочный зал с витринами"
    assert isinstance(test_location.case_id, UUID)
    assert test_location.visited is False
    assert test_location.visit_notes == []
    assert test_location.visited_at is None


def test_evidence_creation(test_evidence):
    """Тест создания улики."""
    assert isinstance(test_evidence.id, UUID)
    assert test_evidence.title == "Отпечатки пальцев"
    assert test_evidence.description == "Отпечатки пальцев на разбитой витрине"
    assert isinstance(test_evidence.case_id, UUID)
    assert test_evidence.location == "Главный зал музея"
    assert test_evidence.type == EvidenceType.PHYSICAL
    assert test_evidence.examined is False
    assert test_evidence.examination_notes == []


def test_suspect_creation(test_suspect):
    """Тест создания подозреваемого."""
    assert isinstance(test_suspect.id, UUID)
    assert test_suspect.name == "Иван Петров"
    assert test_suspect.description == "Бывший сотрудник музея"
    assert test_suspect.case_id == str(test_suspect.case_id)
    assert test_suspect.interrogation_state == "not_interrogated"
    assert test_suspect.interrogation_notes == []
    assert test_suspect.interrogation_cooldown_until is None
    assert test_suspect.status == SuspectStatus.UNKNOWN


def test_case_add_evidence(test_case, test_evidence):
    """Тест добавления улики в дело."""
    test_case.add_evidence(test_evidence)
    assert test_evidence in test_case.evidence
    assert test_evidence.case_id == test_case.id


def test_case_add_location(test_case, test_location):
    """Тест добавления локации в дело."""
    test_case.add_location(test_location)
    assert test_location in test_case.locations
    assert test_location.case_id == test_case.id


def test_case_add_suspect(test_case, test_suspect):
    """Тест добавления подозреваемого в дело."""
    test_case.add_suspect(test_suspect)
    assert test_suspect in test_case.suspects
    assert test_suspect.case_id == str(test_case.id)


def test_location_visit(test_location):
    """Тест посещения локации."""
    notes = "Обнаружены следы взлома"
    test_location.visit(notes)
    assert test_location.visited is True
    assert notes in test_location.visit_notes
    assert isinstance(test_location.visited_at, datetime)


def test_evidence_examine(test_evidence):
    """Тест исследования улики."""
    notes = "Отпечатки принадлежат сотруднику музея"
    test_evidence.examine(notes)
    assert test_evidence.examined is True
    assert notes in test_evidence.examination_notes


def test_suspect_interrogate(test_suspect):
    """Тест допроса подозреваемого."""
    notes = "Подозреваемый отрицает свою причастность"
    test_suspect.interrogate(notes)
    assert test_suspect.interrogation_state == "interrogated"
    assert notes in test_suspect.interrogation_notes
    assert isinstance(test_suspect.interrogation_cooldown_until, datetime)


def test_suspect_interrogation_cooldown(test_suspect):
    """Тест периода ожидания между допросами."""
    notes = "Первый допрос"
    test_suspect.interrogate(notes)

    # Попытка допросить снова должна вызвать исключение
    with pytest.raises(SuspectInterrogationError):
        test_suspect.interrogate("Второй допрос")


def test_case_solve(test_case):
    """Тест завершения дела."""
    solution = "Ограбление совершил бывший сотрудник музея"
    test_case.solve(solution)
    assert test_case.status == CaseStatus.SOLVED
    assert test_case.solution == solution
    assert isinstance(test_case.solved_at, datetime)


def test_evidence_relationships(test_case, test_evidence, test_suspect):
    """Тест связей между уликами и подозреваемыми."""
    # Добавляем улику и подозреваемого в дело
    test_case.add_evidence(test_evidence)
    test_case.add_suspect(test_suspect)

    # Связываем улику с подозреваемым
    test_evidence.link_to_suspect(test_suspect.id)
    test_suspect.add_evidence(test_evidence.id)

    assert test_suspect.id in test_evidence.related_suspect_ids
    assert test_evidence.id in test_suspect.evidence_ids


def test_location_evidence_management(test_location, test_evidence):
    """Тест управления уликами в локации."""
    # Добавляем улику в локацию
    test_location.add_evidence(test_evidence)
    assert test_evidence.id in test_location.evidence_ids
    assert test_evidence in test_location.evidence

    # Удаляем улику из локации
    test_location.remove_evidence(test_evidence)
    assert test_evidence.id not in test_location.evidence_ids
    assert test_evidence not in test_location.evidence


def test_suspect_status_update(test_suspect):
    """Тест обновления статуса подозреваемого."""
    # Изначальный статус
    assert test_suspect.status == SuspectStatus.UNKNOWN

    # Обновляем статус
    test_suspect.update_status(SuspectStatus.SUSPECT)
    assert test_suspect.status == SuspectStatus.SUSPECT

    # Очищаем подозрения
    test_suspect.update_status(SuspectStatus.CLEARED)
    assert test_suspect.status == SuspectStatus.CLEARED


def test_case_progress_tracking(test_case, test_evidence, test_location, test_suspect):
    """Тест отслеживания прогресса расследования."""
    # Добавляем элементы в дело
    test_case.add_evidence(test_evidence)
    test_case.add_location(test_location)
    test_case.add_suspect(test_suspect)

    # Исследуем улику
    test_evidence.examine("Важная улика")

    # Посещаем локацию
    test_location.visit("Осмотр места преступления")

    # Допрашиваем подозреваемого
    test_suspect.interrogate("Допрос подозреваемого")

    # Проверяем прогресс
    progress = test_case.calculate_progress()
    assert 0 <= progress <= 1  # Прогресс должен быть между 0 и 1
    assert progress > 0  # Прогресс должен увеличиться после выполнения действий
