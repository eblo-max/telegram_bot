"""Основной класс Telegram бота."""

from typing import Dict, Optional
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from dark_archive.domain.entities.case import Case, CaseDifficulty
from dark_archive.domain.entities.player import Player
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect
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


class DarkArchiveBot:
    """Основной класс бота Dark Archive."""

    def __init__(self, token: str):
        """Инициализация бота."""
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.players: Dict[int, Player] = {}
        self.user_states: Dict[int, str] = {}
        self.temp_data: Dict[int, Dict] = {}

        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Настройка обработчиков команд."""
        # Базовые команды
        self.dp.message.register(self._handle_start, Command("start"))
        self.dp.message.register(self._handle_help, Command("help"))

        # Команды управления делами
        self.dp.message.register(self._handle_new_case, Command("new_case"))
        self.dp.message.register(self._handle_cases, Command("cases"))
        self.dp.message.register(self._handle_case, Command("case"))
        self.dp.message.register(self._handle_solve, Command("solve"))

        # Команды расследования
        self.dp.message.register(self._handle_examine, Command("examine"))
        self.dp.message.register(self._handle_visit, Command("visit"))
        self.dp.message.register(self._handle_interrogate, Command("interrogate"))

        # Команды прогресса
        self.dp.message.register(self._handle_progress, Command("progress"))
        self.dp.message.register(self._handle_notes, Command("notes"))
        self.dp.message.register(self._handle_theories, Command("theories"))

        # Прочие команды
        self.dp.message.register(self._handle_profile, Command("profile"))

    async def _handle_start(self, message: Message) -> None:
        """Обработчик команды /start."""
        try:
            user_id = message.from_user.id
            if user_id not in self.players:
                self.players[user_id] = Player.create(
                    telegram_id=user_id,
                    username=message.from_user.username or str(user_id),
                    role="detective",
                )
            await handle_start_command(self.bot, message)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_help(self, message: Message) -> None:
        """Обработчик команды /help."""
        try:
            await handle_help_command(self.bot, message)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_new_case(self, message: Message) -> None:
        """Обработчик команды /new_case."""
        try:
            user_id = message.from_user.id
            self.user_states[user_id] = "waiting_case_title"
            self.temp_data[user_id] = {}
            await handle_new_case_command(self.bot, message)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_cases(self, message: Message) -> None:
        """Обработчик команды /cases."""
        try:
            player = self._get_player(message)
            cases_text = "Ваши дела:\n\n"
            # TODO: Добавить получение списка дел игрока
            await self.bot.send_message(message.chat.id, cases_text)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_case(self, message: Message) -> None:
        """Обработчик команды /case."""
        try:
            player = self._get_player(message)
            if not player.active_case_id:
                raise CaseNotFoundError("У вас нет активного дела")
            # TODO: Добавить получение информации о деле
            case_info = "Информация о деле:\n\n"
            await self.bot.send_message(message.chat.id, case_info)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_solve(self, message: Message) -> None:
        """Обработчик команды /solve."""
        try:
            player = self._get_player(message)
            if not player.active_case_id:
                raise CaseNotFoundError("У вас нет активного дела")
            self.user_states[message.from_user.id] = "waiting_solution"
            await handle_solve_command(self.bot, message)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_examine(self, message: Message) -> None:
        """Обработчик команды /examine."""
        try:
            player = self._get_player(message)
            if not player.active_case_id:
                raise CaseNotFoundError("У вас нет активного дела")
            # TODO: Добавить проверку существования улики
            self.user_states[message.from_user.id] = "waiting_examination_notes"
            await handle_examine_command(self.bot, message)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_visit(self, message: Message) -> None:
        """Обработчик команды /visit."""
        try:
            player = self._get_player(message)
            if not player.active_case_id:
                raise CaseNotFoundError("У вас нет активного дела")
            # TODO: Добавить проверку существования локации
            self.user_states[message.from_user.id] = "waiting_visit_notes"
            await handle_visit_command(self.bot, message)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_interrogate(self, message: Message) -> None:
        """Обработчик команды /interrogate."""
        try:
            player = self._get_player(message)
            if not player.active_case_id:
                raise CaseNotFoundError("У вас нет активного дела")
            # TODO: Добавить проверку существования подозреваемого
            self.user_states[message.from_user.id] = "waiting_interrogation_questions"
            await handle_interrogate_command(self.bot, message)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_progress(self, message: Message) -> None:
        """Обработчик команды /progress."""
        try:
            player = self._get_player(message)
            if not player.active_case_id:
                raise CaseNotFoundError("У вас нет активного дела")
            # TODO: Добавить получение прогресса расследования
            progress_text = "Прогресс расследования:\n\n"
            await self.bot.send_message(message.chat.id, progress_text)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_notes(self, message: Message) -> None:
        """Обработчик команды /notes."""
        try:
            player = self._get_player(message)
            if not player.active_case_id:
                raise CaseNotFoundError("У вас нет активного дела")
            # TODO: Добавить получение заметок по делу
            notes_text = "Ваши заметки по делу:\n\n"
            await self.bot.send_message(message.chat.id, notes_text)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_theories(self, message: Message) -> None:
        """Обработчик команды /theories."""
        try:
            player = self._get_player(message)
            if not player.active_case_id:
                raise CaseNotFoundError("У вас нет активного дела")
            # TODO: Добавить получение теорий по делу
            theories_text = "Ваши теории по делу:\n\n"
            await self.bot.send_message(message.chat.id, theories_text)
        except Exception as e:
            await handle_error(self.bot, message, e)

    async def _handle_profile(self, message: Message) -> None:
        """Обработчик команды /profile."""
        try:
            player = self._get_player(message)
            profile_text = f"""
            Ваш профиль:
            
            👤 Имя: {player.username}
            🎭 Роль: {player.role}
            📊 Раскрытых дел: {len(player.solved_cases)}
            """
            await self.bot.send_message(message.chat.id, profile_text)
        except Exception as e:
            await handle_error(self.bot, message, e)

    def _get_player(self, message: Message) -> Player:
        """Получение игрока по сообщению."""
        user_id = message.from_user.id
        if user_id not in self.players:
            raise AccessDeniedError("Вы не зарегистрированы в системе")
        return self.players[user_id]

    async def start(self) -> None:
        """Запуск бота."""
        await self.dp.start_polling(self.bot)

    async def stop(self) -> None:
        """Остановка бота."""
        await self.bot.session.close()
