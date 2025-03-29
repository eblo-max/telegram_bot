"""Обработчики команд Telegram бота."""

from typing import Optional
from aiogram import Bot
from aiogram.types import Message

from dark_archive.domain.entities.case import Case, CaseDifficulty, CaseStatus
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.entities.player import Player
from dark_archive.domain.exceptions import (
    AccessDeniedError,
    CaseNotFoundError,
    EvidenceNotFoundError,
    SuspectNotFoundError,
)


async def handle_start_command(bot: Bot, message: Message) -> None:
    """Обработчик команды /start."""
    welcome_text = """
    Добро пожаловать в Dark Archive - игру о расследовании преступлений! 🕵️‍♂️

    Здесь вы сможете:
    - Расследовать сложные дела 🔍
    - Собирать и анализировать улики 🔬
    - Допрашивать подозреваемых 👥
    - Посещать места преступлений 🏛
    
    Используйте /help для просмотра списка доступных команд.
    """
    await bot.send_message(message.chat.id, welcome_text)


async def handle_help_command(bot: Bot, message: Message) -> None:
    """Обработчик команды /help."""
    help_text = """
    Список доступных команд:
    
    📋 Управление делами:
    /new_case - Создать новое дело
    /cases - Список ваших дел
    /case - Информация о текущем деле
    /solve - Предложить решение дела
    
    🔍 Расследование:
    /examine <id> - Исследовать улику
    /visit <id> - Посетить локацию
    /interrogate <id> - Допросить подозреваемого
    
    📊 Прогресс:
    /progress - Показать прогресс расследования
    /notes - Ваши заметки по делу
    /theories - Ваши теории
    
    ℹ️ Прочее:
    /help - Показать это сообщение
    /profile - Ваш профиль
    """
    await bot.send_message(message.chat.id, help_text)


async def handle_new_case_command(bot: Bot, message: Message) -> None:
    """Обработчик команды создания нового дела."""
    await bot.send_message(
        message.chat.id,
        "Введите название дела:",
    )


async def handle_case_title(bot: Bot, message: Message) -> None:
    """Обработчик ввода названия дела."""
    await bot.send_message(
        message.chat.id,
        "Введите описание дела:",
    )


async def handle_case_description(bot: Bot, message: Message) -> None:
    """Обработчик ввода описания дела."""
    difficulty_text = """
    Выберите сложность дела:
    
    EASY - Легкое дело
    MEDIUM - Дело средней сложности
    HARD - Сложное дело
    
    Введите EASY, MEDIUM или HARD:
    """
    await bot.send_message(message.chat.id, difficulty_text)


async def handle_case_difficulty(bot: Bot, message: Message) -> None:
    """Обработчик выбора сложности дела."""
    await bot.send_message(
        message.chat.id,
        "Дело успешно создано! Используйте /case для просмотра информации о деле.",
    )


async def handle_examine_command(bot: Bot, message: Message) -> None:
    """Обработчик команды исследования улики."""
    await bot.send_message(
        message.chat.id,
        "Исследование улики. Введите ваши заметки об исследовании:",
    )


async def handle_examination_notes(
    bot: Bot, message: Message, evidence: Evidence
) -> None:
    """Обработчик ввода заметок об исследовании."""
    evidence.examine(message.text)
    await bot.send_message(
        message.chat.id,
        "Улика успешно исследована! Используйте /case для просмотра обновленной информации.",
    )


async def handle_interrogate_command(bot: Bot, message: Message) -> None:
    """Обработчик команды допроса подозреваемого."""
    await bot.send_message(
        message.chat.id,
        "Допрос подозреваемого. Введите ваши вопросы:",
    )


async def handle_interrogation_questions(
    bot: Bot, message: Message, suspect: Suspect
) -> None:
    """Обработчик ввода вопросов для допроса."""
    suspect.interrogate(message.text)
    await bot.send_message(
        message.chat.id,
        "Допрос успешно проведен! Используйте /case для просмотра обновленной информации.",
    )


async def handle_visit_command(bot: Bot, message: Message) -> None:
    """Обработчик команды посещения локации."""
    await bot.send_message(
        message.chat.id,
        "Осмотр локации. Введите ваши наблюдения:",
    )


async def handle_visit_notes(bot: Bot, message: Message, location: Location) -> None:
    """Обработчик ввода заметок о посещении."""
    location.visit(message.text)
    await bot.send_message(
        message.chat.id,
        "Локация успешно осмотрена! Используйте /case для просмотра обновленной информации.",
    )


async def handle_solve_command(bot: Bot, message: Message) -> None:
    """Обработчик команды решения дела."""
    await bot.send_message(
        message.chat.id,
        "Введите решение дела:",
    )


async def handle_case_solution(bot: Bot, message: Message, case: Case) -> None:
    """Обработчик ввода решения дела."""
    case.solve(message.text)
    await bot.send_message(
        message.chat.id,
        "Дело успешно раскрыто! Поздравляем с успешным завершением расследования! 🎉",
    )


async def handle_error(bot: Bot, message: Message, error: Exception) -> None:
    """Обработчик ошибок."""
    error_messages = {
        AccessDeniedError: "У вас нет доступа к этому делу",
        CaseNotFoundError: "Дело не найдено",
        EvidenceNotFoundError: "Улика не найдена",
        SuspectNotFoundError: "Подозреваемый не найден",
    }

    error_text = error_messages.get(type(error), str(error))
    await bot.send_message(message.chat.id, f"❌ Ошибка: {error_text}")
