"""Тесты пользовательских сценариев в Telegram."""

import pytest
from datetime import datetime
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock

from dark_archive.domain.entities.case import Case, CaseDifficulty, CaseStatus
from dark_archive.domain.entities.evidence import Evidence, EvidenceType
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect, SuspectStatus
from dark_archive.domain.entities.player import Player, PlayerRole
from dark_archive.domain.exceptions import (
    AccessDeniedError,
    CaseNotFoundError,
    EvidenceNotFoundError,
    SuspectNotFoundError,
)
from dark_archive.telegram.handlers import (
    handle_start_command,
    handle_help_command,
    handle_new_case_command,
    handle_case_title,
    handle_case_description,
    handle_case_difficulty,
    handle_examine_command,
    handle_examination_notes,
    handle_interrogate_command,
    handle_interrogation_questions,
    handle_visit_command,
    handle_visit_notes,
    handle_solve_command,
    handle_case_solution,
    handle_error,
)


@pytest.fixture
def telegram_message():
    """Фикстура для имитации сообщения Telegram."""
    message = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "detective_user"
    message.text = ""
    return message


@pytest.fixture
def telegram_bot():
    """Фикстура для имитации бота Telegram."""
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.edit_message_text = AsyncMock()
    return bot


@pytest.fixture
def player():
    """Фикстура для тестового игрока."""
    return Player.create(
        telegram_id=12345,
        username="detective_user",
        role=PlayerRole.DETECTIVE,
    )


@pytest.fixture
def test_case():
    """Фикстура для тестового дела."""
    return Case.create(
        title="Ограбление музея",
        description="В городском музее произошло ограбление",
        difficulty=CaseDifficulty.MEDIUM,
    )


@pytest.mark.asyncio
async def test_start_command(telegram_bot, telegram_message, player):
    """Тест команды /start."""
    # Имитируем отправку команды /start
    telegram_message.text = "/start"

    # Проверяем, что бот отправляет приветственное сообщение
    await handle_start_command(telegram_bot, telegram_message)

    telegram_bot.send_message.assert_called_once()
    assert (
        "Добро пожаловать в Dark Archive" in telegram_bot.send_message.call_args[0][1]
    )


@pytest.mark.asyncio
async def test_help_command(telegram_bot, telegram_message):
    """Тест команды /help."""
    telegram_message.text = "/help"

    await handle_help_command(telegram_bot, telegram_message)

    telegram_bot.send_message.assert_called_once()
    assert "Список доступных команд" in telegram_bot.send_message.call_args[0][1]


@pytest.mark.asyncio
async def test_case_creation_flow(telegram_bot, telegram_message, player):
    """Тест сценария создания нового дела."""
    # Шаг 1: Начало создания дела
    telegram_message.text = "/new_case"
    await handle_new_case_command(telegram_bot, telegram_message)

    assert telegram_bot.send_message.call_count == 1
    assert "Введите название дела" in telegram_bot.send_message.call_args[0][1]

    # Шаг 2: Ввод названия дела
    telegram_message.text = "Ограбление музея"
    await handle_case_title(telegram_bot, telegram_message)

    assert telegram_bot.send_message.call_count == 2
    assert "Введите описание дела" in telegram_bot.send_message.call_args[0][1]

    # Шаг 3: Ввод описания дела
    telegram_message.text = "В городском музее произошло ограбление"
    await handle_case_description(telegram_bot, telegram_message)

    assert telegram_bot.send_message.call_count == 3
    assert "Выберите сложность дела" in telegram_bot.send_message.call_args[0][1]

    # Шаг 4: Выбор сложности
    telegram_message.text = "MEDIUM"
    await handle_case_difficulty(telegram_bot, telegram_message)

    assert telegram_bot.send_message.call_count == 4
    assert "Дело успешно создано" in telegram_bot.send_message.call_args[0][1]


@pytest.mark.asyncio
async def test_evidence_examination_flow(
    telegram_bot, telegram_message, player, test_case
):
    """Тест сценария исследования улики."""
    # Создаем тестовую улику
    evidence = Evidence.create(
        title="Отпечатки пальцев",
        description="Отпечатки пальцев на разбитой витрине",
        case_id=test_case.id,
        location="Главный зал музея",
        type=EvidenceType.PHYSICAL,
    )
    test_case.add_evidence(evidence)
    player.active_case_id = test_case.id

    # Шаг 1: Команда исследования улики
    telegram_message.text = f"/examine {evidence.id}"
    await handle_examine_command(telegram_bot, telegram_message)

    assert telegram_bot.send_message.call_count == 1
    assert "Исследование улики" in telegram_bot.send_message.call_args[0][1]

    # Шаг 2: Ввод заметок об исследовании
    telegram_message.text = "На отпечатках видны характерные следы"
    await handle_examination_notes(telegram_bot, telegram_message, evidence)

    assert telegram_bot.send_message.call_count == 2
    assert "Улика успешно исследована" in telegram_bot.send_message.call_args[0][1]
    assert evidence.examined
    assert "На отпечатках видны характерные следы" in evidence.examination_notes


@pytest.mark.asyncio
async def test_suspect_interrogation_flow(
    telegram_bot, telegram_message, player, test_case
):
    """Тест сценария допроса подозреваемого."""
    # Создаем тестового подозреваемого
    suspect = Suspect.create(
        name="Иван Петров",
        description="Бывший сотрудник музея",
        case_id=str(test_case.id),
    )
    test_case.add_suspect(suspect)
    player.active_case_id = test_case.id

    # Шаг 1: Команда допроса
    telegram_message.text = f"/interrogate {suspect.id}"
    await handle_interrogate_command(telegram_bot, telegram_message)

    assert telegram_bot.send_message.call_count == 1
    assert "Допрос подозреваемого" in telegram_bot.send_message.call_args[0][1]

    # Шаг 2: Ввод вопросов для допроса
    telegram_message.text = "Где вы были во время ограбления?"
    await handle_interrogation_questions(telegram_bot, telegram_message, suspect)

    assert telegram_bot.send_message.call_count == 2
    assert "Допрос успешно проведен" in telegram_bot.send_message.call_args[0][1]
    assert suspect.interrogation_state == "interrogated"
    assert "Где вы были во время ограбления?" in suspect.interrogation_notes


@pytest.mark.asyncio
async def test_location_visit_flow(telegram_bot, telegram_message, player, test_case):
    """Тест сценария посещения локации."""
    # Создаем тестовую локацию
    location = Location.create(
        name="Главный зал музея",
        description="Центральный выставочный зал с витринами",
        case_id=test_case.id,
    )
    test_case.add_location(location)
    player.active_case_id = test_case.id

    # Шаг 1: Команда посещения локации
    telegram_message.text = f"/visit {location.id}"
    await handle_visit_command(telegram_bot, telegram_message)

    assert telegram_bot.send_message.call_count == 1
    assert "Осмотр локации" in telegram_bot.send_message.call_args[0][1]

    # Шаг 2: Ввод заметок о посещении
    telegram_message.text = "Обнаружены следы взлома на витрине"
    await handle_visit_notes(telegram_bot, telegram_message, location)

    assert telegram_bot.send_message.call_count == 2
    assert "Локация успешно осмотрена" in telegram_bot.send_message.call_args[0][1]
    assert location.visited
    assert "Обнаружены следы взлома на витрине" in location.visit_notes


@pytest.mark.asyncio
async def test_case_solving_flow(telegram_bot, telegram_message, player, test_case):
    """Тест сценария решения дела."""
    player.active_case_id = test_case.id

    # Шаг 1: Команда решения дела
    telegram_message.text = "/solve"
    await handle_solve_command(telegram_bot, telegram_message)

    assert telegram_bot.send_message.call_count == 1
    assert "Введите решение дела" in telegram_bot.send_message.call_args[0][1]

    # Шаг 2: Ввод решения
    telegram_message.text = "Ограбление совершил бывший сотрудник музея Иван Петров"
    await handle_case_solution(telegram_bot, telegram_message, test_case)

    assert telegram_bot.send_message.call_count == 2
    assert "Дело успешно раскрыто" in telegram_bot.send_message.call_args[0][1]
    assert test_case.status == CaseStatus.SOLVED
    assert (
        test_case.solution == "Ограбление совершил бывший сотрудник музея Иван Петров"
    )


@pytest.mark.asyncio
async def test_error_handling(telegram_bot, telegram_message, player):
    """Тест обработки ошибок."""

    # Тест ошибки доступа
    async def test_access_denied():
        raise AccessDeniedError("У вас нет доступа к этому делу")

    await handle_error(
        telegram_bot,
        telegram_message,
        AccessDeniedError("У вас нет доступа к этому делу"),
    )
    assert "У вас нет доступа к этому делу" in telegram_bot.send_message.call_args[0][1]

    # Тест ошибки не найденного дела
    await handle_error(
        telegram_bot, telegram_message, CaseNotFoundError("Дело не найдено")
    )
    assert "Дело не найдено" in telegram_bot.send_message.call_args[0][1]

    # Тест ошибки не найденной улики
    await handle_error(
        telegram_bot, telegram_message, EvidenceNotFoundError("Улика не найдена")
    )
    assert "Улика не найдена" in telegram_bot.send_message.call_args[0][1]

    # Тест ошибки не найденного подозреваемого
    await handle_error(
        telegram_bot, telegram_message, SuspectNotFoundError("Подозреваемый не найден")
    )
    assert "Подозреваемый не найден" in telegram_bot.send_message.call_args[0][1]
