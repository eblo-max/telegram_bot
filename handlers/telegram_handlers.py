import logging
from typing import Dict, List, Optional
from uuid import UUID

from telegram import Update
from telegram.ext import ContextTypes

from dark_archive.application.services.case_service import CaseService
from dark_archive.domain.models.case import Case, CaseStatus, Location
from dark_archive.application.interfaces.ai_service import IAIService

logger = logging.getLogger(__name__)


class TelegramHandlers:
    """Обработчики команд для Telegram бота"""

    def __init__(self, case_service: CaseService, ai_service: IAIService):
        self.case_service = case_service
        self.ai_service = ai_service
        self._user_states: Dict[int, UUID] = {}  # user_id -> active_case_id

    async def start_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        await update.message.reply_text(
            "Добро пожаловать в Dark Archive Bot!\n\n"
            "Я помогу вам расследовать загадочные дела. "
            "Используйте следующие команды:\n"
            "/new_case - Начать новое расследование\n"
            "/cases - Посмотреть список активных дел\n"
            "/help - Показать справку"
        )

    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /help"""
        await update.message.reply_text(
            "Список доступных команд:\n\n"
            "/new_case - Начать новое расследование\n"
            "/cases - Посмотреть список активных дел\n"
            "/case - Информация о текущем деле\n"
            "/locations - Список доступных локаций\n"
            "/evidence - Список найденных улик\n"
            "/analyze <id> - Анализировать улику\n"
            "/theory - Предложить теорию\n"
            "/hint - Получить подсказку"
        )

    async def new_case_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /new_case"""
        try:
            user_id = update.effective_user.id
            logger.info(f"Creating new case for user {user_id}")

            # Отправляем сообщение о начале генерации
            await update.message.reply_text(
                "🔍 Генерирую новое расследование...", parse_mode="Markdown"
            )

            # Генерируем новое дело
            case = await self.case_service.create_case()

            if not case:
                logger.error("Failed to create case - case_service returned None")
                await update.message.reply_text(
                    "❌ Произошла ошибка при создании дела. Пожалуйста, попробуйте позже.",
                    parse_mode="Markdown",
                )
                return

            # Устанавливаем как активное дело для пользователя
            self._user_states[user_id] = case.id

            # Форматируем сообщение о созданном деле
            case_message = (
                f"📁 *Новое дело создано!*\n\n"
                f"*Название:* {case.title}\n"
                f"*Описание:* {case.description}\n\n"
                f"*Сложность:* {case.difficulty}/10\n"
                f"*Начальная локация:* {case.initial_location.name}\n\n"
                f"Используйте /case для получения подробной информации."
            )

            await update.message.reply_text(case_message, parse_mode="Markdown")
            logger.info(f"Successfully created case {case.id} for user {user_id}")

        except Exception as e:
            logger.error(f"Error in new_case_command: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Произошла ошибка при создании дела. Пожалуйста, попробуйте позже.",
                parse_mode="Markdown",
            )

    async def cases_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /cases"""
        cases = await self.case_service.get_cases_by_status(CaseStatus.IN_PROGRESS)
        if not cases:
            await update.message.reply_text("У вас пока нет активных расследований.")
            return

        cases_text = "Ваши активные расследования:\n\n"
        for case in cases:
            cases_text += f"📁 {case.title}\n"
            cases_text += f"Статус: {case.status.value}\n"
            cases_text += f"Сложность: {case.difficulty}/10\n\n"

        await update.message.reply_text(cases_text)

    async def case_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /case"""
        user_id = update.effective_user.id
        case_id = self._user_states.get(user_id)

        if not case_id:
            await update.message.reply_text(
                "У вас нет активного расследования.\n"
                "Используйте /new_case чтобы начать новое."
            )
            return

        case = await self.case_service.get_case(case_id)
        if not case:
            await update.message.reply_text(
                "Произошла ошибка при получении информации о деле."
            )
            return

        discovered_locations = [loc for loc in case.locations if loc.discovered]
        discovered_evidence = [ev for ev in case.evidence if ev.discovered]

        case_text = f"📁 {case.title}\n\n"
        case_text += f"Описание: {case.description}\n"
        case_text += f"Статус: {case.status.value}\n"
        case_text += f"Сложность: {case.difficulty}/10\n\n"
        case_text += (
            f"Исследовано локаций: {len(discovered_locations)}/{len(case.locations)}\n"
        )
        case_text += f"Найдено улик: {len(discovered_evidence)}/{len(case.evidence)}\n"

        await update.message.reply_text(case_text)

    async def locations_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /locations"""
        user_id = update.effective_user.id
        case_id = self._user_states.get(user_id)

        if not case_id:
            await update.message.reply_text(
                "Сначала начните расследование с помощью /new_case"
            )
            return

        case = await self.case_service.get_case(case_id)
        if not case:
            await update.message.reply_text(
                "Произошла ошибка при получении информации о деле."
            )
            return

        locations_text = "Доступные локации:\n\n"
        for location in case.locations:
            if location.discovered:
                locations_text += f"📍 {location.name}\n"
                locations_text += f"Уровень риска: {location.risk_level}/10\n"
                description = await self.ai_service.generate_location_description(
                    case,
                    location,
                    [
                        ev
                        for ev in case.evidence
                        if ev.location_id == location.id and ev.discovered
                    ],
                )
                locations_text += f"{description}\n\n"
            else:
                locations_text += f"❓ Неизвестная локация\n\n"

        await update.message.reply_text(locations_text)

    async def hint_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Обработчик команды /hint"""
        user_id = update.effective_user.id
        case_id = self._user_states.get(user_id)

        if not case_id:
            await update.message.reply_text(
                "Сначала начните расследование с помощью /new_case"
            )
            return

        case = await self.case_service.get_case(case_id)
        if not case:
            await update.message.reply_text(
                "Произошла ошибка при получении информации о деле."
            )
            return

        discovered_evidence = [ev for ev in case.evidence if ev.discovered]
        current_progress = (
            len(discovered_evidence) / len(case.evidence) if case.evidence else 0
        )

        hint = await self.ai_service.generate_hint(
            case, current_progress, discovered_evidence
        )
        await update.message.reply_text(f"💡 Подсказка: {hint}")
