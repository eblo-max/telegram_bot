"""Интеграционные тесты для ClaudeAIService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import datetime

from dark_archive.infrastructure.ai.claude_service import ClaudeAIService
from dark_archive.domain.entities.case import Case, CaseDifficulty
from dark_archive.domain.entities.evidence import Evidence, EvidenceType
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect, SuspectStatus


@pytest.fixture
def mock_anthropic_client():
    """Мок для клиента Anthropic."""
    client = MagicMock()
    client.messages.create = AsyncMock()
    return client


@pytest.fixture
def ai_service(mock_anthropic_client):
    """Фикстура для AI сервиса."""
    service = ClaudeAIService("test_api_key")
    service.client = mock_anthropic_client
    return service


@pytest.fixture
def test_case():
    """Фикстура для тестового дела."""
    return Case.create(
        title="Ограбление музея",
        description="В городском музее произошло ограбление",
        difficulty=CaseDifficulty.MEDIUM,
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
def test_location():
    """Фикстура для тестовой локации."""
    return Location.create(
        name="Главный зал музея",
        description="Центральный выставочный зал с витринами",
        case_id=uuid4(),
    )


@pytest.fixture
def test_suspect():
    """Фикстура для тестового подозреваемого."""
    return Suspect.create(
        name="Иван Петров",
        description="Бывший сотрудник музея",
        case_id=str(uuid4()),
    )


@pytest.mark.asyncio
async def test_generate_case(ai_service, mock_anthropic_client):
    """Тест генерации нового дела."""
    mock_response = MagicMock()
    mock_response.content = {
        "title": "Ограбление музея",
        "description": "В городском музее произошло ограбление",
        "suspects": [
            {"name": "Иван Петров", "description": "Бывший сотрудник музея"},
            {"name": "Анна Сидорова", "description": "Куратор выставки"},
        ],
        "evidence": [
            {"title": "Отпечатки пальцев", "description": "На разбитой витрине"},
            {"title": "Записка", "description": "С требованием выкупа"},
        ],
        "locations": [
            {"name": "Главный зал", "description": "Место преступления"},
            {"name": "Служебный вход", "description": "Точка проникновения"},
        ],
        "solution": "Ограбление совершил бывший сотрудник музея",
    }
    mock_anthropic_client.messages.create.return_value = mock_response

    result = await ai_service.generate_case(difficulty=5)
    assert result == mock_response.content
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_evidence(
    ai_service, mock_anthropic_client, test_case, test_evidence
):
    """Тест анализа улики."""
    mock_response = MagicMock()
    mock_response.content = (
        "Анализ улики: отпечатки пальцев принадлежат сотруднику музея"
    )
    mock_anthropic_client.messages.create.return_value = mock_response

    result = await ai_service.analyze_evidence(test_case, test_evidence)
    assert result == mock_response.content
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_location_description(
    ai_service, mock_anthropic_client, test_case, test_location, test_evidence
):
    """Тест генерации описания локации."""
    mock_response = MagicMock()
    mock_response.content = "Описание локации: главный зал музея с разбитыми витринами"
    mock_anthropic_client.messages.create.return_value = mock_response

    result = await ai_service.generate_location_description(
        test_case, test_location, [test_evidence]
    )
    assert result == mock_response.content
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_evaluate_theory(ai_service, mock_anthropic_client, test_case):
    """Тест оценки теории."""
    mock_response = MagicMock()
    mock_response.content = {
        "accuracy": 0.8,
        "completeness": 0.7,
        "coherence": 0.9,
    }
    mock_anthropic_client.messages.create.return_value = mock_response

    theory = "Ограбление совершил бывший сотрудник музея, используя свой пропуск"
    result = await ai_service.evaluate_theory(test_case, theory, [uuid4()])
    assert result == mock_response.content
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_hint(
    ai_service, mock_anthropic_client, test_case, test_evidence
):
    """Тест генерации подсказки."""
    mock_response = MagicMock()
    mock_response.content = "Обратите внимание на систему контроля доступа"
    mock_anthropic_client.messages.create.return_value = mock_response

    result = await ai_service.generate_hint(test_case, 0.5, [test_evidence])
    assert result == mock_response.content
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_suspect(
    ai_service, mock_anthropic_client, test_case, test_suspect, test_evidence
):
    """Тест анализа подозреваемого."""
    mock_response = MagicMock()
    mock_response.content = {
        "alibi_credibility": "Низкая",
        "motive_analysis": "Имеет сильный мотив",
        "evidence_connection": "Прямая связь с уликами",
        "suspicion_level": "Высокий",
    }
    mock_anthropic_client.messages.create.return_value = mock_response

    result = await ai_service.analyze_suspect(test_case, test_suspect, [test_evidence])
    assert result == mock_response.content
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_generate_interrogation(
    ai_service, mock_anthropic_client, test_case, test_suspect, test_evidence
):
    """Тест генерации допроса."""
    mock_response = MagicMock()
    mock_response.content = [
        {"question": "Где вы были вечером?", "answer": "В кино"},
        {"question": "С кем можете подтвердить?", "answer": "Был один"},
    ]
    mock_anthropic_client.messages.create.return_value = mock_response

    result = await ai_service.generate_interrogation(
        test_case, test_suspect, [test_evidence]
    )
    assert result == mock_response.content
    mock_anthropic_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_error_handling(
    ai_service,
    mock_anthropic_client,
    test_case,
    test_evidence,
    test_location,
    test_suspect,
):
    """Тест обработки ошибок."""
    mock_anthropic_client.messages.create.side_effect = Exception("API Error")

    # Тест генерации дела
    result = await ai_service.generate_case()
    assert result is None

    # Тест анализа улики
    result = await ai_service.analyze_evidence(test_case, test_evidence)
    assert result == "Не удалось проанализировать улику"

    # Тест генерации описания локации
    result = await ai_service.generate_location_description(
        test_case, test_location, []
    )
    assert result == "Не удалось сгенерировать описание локации"

    # Тест оценки теории
    result = await ai_service.evaluate_theory(test_case, "теория", [])
    assert result == {"accuracy": 0.0, "completeness": 0.0, "coherence": 0.0}

    # Тест генерации подсказки
    result = await ai_service.generate_hint(test_case, 0.5, [])
    assert result == "Не удалось сгенерировать подсказку"

    # Тест анализа подозреваемого
    result = await ai_service.analyze_suspect(test_case, test_suspect, [])
    assert result == {
        "alibi_credibility": "Не удалось оценить",
        "motive_analysis": "Не удалось проанализировать",
        "evidence_connection": "Не удалось установить",
        "suspicion_level": "Не удалось определить",
    }

    # Тест генерации допроса
    result = await ai_service.generate_interrogation(test_case, test_suspect, [])
    assert result == [
        {"question": "Ошибка", "answer": "Не удалось сгенерировать допрос"}
    ]
