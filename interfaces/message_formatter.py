from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.location import Location
from dark_archive.domain.entities.suspect import Suspect
from dark_archive.domain.interfaces.message_service import Button, Message


class MessageFormatter(ABC):
    """Базовый интерфейс для форматтеров сообщений"""

    @abstractmethod
    def format_case_details(self, case: Case) -> Message:
        """Форматирует детали дела

        Args:
            case: Объект дела

        Returns:
            Message: Отформатированное сообщение
        """
        pass

    @abstractmethod
    def format_evidence_list(self, evidence_list: List[Evidence]) -> Message:
        """Форматирует список улик

        Args:
            evidence_list: Список улик

        Returns:
            Message: Отформатированное сообщение
        """
        pass

    @abstractmethod
    def format_location_details(
        self, location: Location, evidence: List[Evidence]
    ) -> Message:
        """Форматирует детали локации

        Args:
            location: Объект локации
            evidence: Список улик в локации

        Returns:
            Message: Отформатированное сообщение
        """
        pass

    @abstractmethod
    def format_suspect_details(
        self, suspect: Suspect, evidence: List[Evidence]
    ) -> Message:
        """Форматирует детали подозреваемого

        Args:
            suspect: Объект подозреваемого
            evidence: Список связанных улик

        Returns:
            Message: Отформатированное сообщение
        """
        pass

    @abstractmethod
    def format_error(self, error: str) -> Message:
        """Форматирует сообщение об ошибке

        Args:
            error: Текст ошибки

        Returns:
            Message: Отформатированное сообщение
        """
        pass


class MarkdownFormatter(MessageFormatter):
    """Форматтер сообщений в формате Markdown"""

    def format_case_details(self, case: Case) -> Message:
        """Форматирует детали дела в Markdown"""
        text = (
            f"📁 *Дело #{case.id}*\n\n"
            f"*Название:* {case.title}\n"
            f"*Описание:* {case.description}\n\n"
            f"*Сложность:* {case.difficulty}/10\n"
            f"*Статус:* {case.status}\n"
            f"*Прогресс:* {case.progress * 100:.1f}%\n\n"
            f"*Локации:* {len(case.locations)}\n"
            f"*Улики:* {len(case.evidence)}\n"
            f"*Подозреваемые:* {len(case.suspects)}\n"
        )

        if case.notes:
            text += "\n*Заметки:*\n" + "\n".join(f"• {note}" for note in case.notes)

        return Message(text=text, parse_mode="Markdown")

    def format_evidence_list(self, evidence_list: List[Evidence]) -> Message:
        """Форматирует список улик в Markdown"""
        if not evidence_list:
            return Message(text="🔍 *Улики не найдены*", parse_mode="Markdown")

        text = "🔍 *Найденные улики:*\n\n"
        for ev in evidence_list:
            text += (
                f"*{ev.name}*\n"
                f"Тип: {ev.type.value}\n"
                f"Важность: {ev.importance}/10\n"
                f"Описание: {ev.description}\n"
            )
            if ev.notes:
                text += f"Заметки: {ev.notes}\n"
            text += "\n"

        return Message(text=text, parse_mode="Markdown")

    def format_location_details(
        self, location: Location, evidence: List[Evidence]
    ) -> Message:
        """Форматирует детали локации в Markdown"""
        text = (
            f"📍 *{location.name}*\n\n"
            f"*Описание:* {location.description}\n"
            f"*Уровень риска:* {location.risk_level}/10\n\n"
        )

        if evidence:
            text += "*Найденные улики:*\n"
            for ev in evidence:
                text += f"• {ev.name}\n"

        if location.notes:
            text += f"\n*Заметки:*\n{location.notes}"

        return Message(text=text, parse_mode="Markdown")

    def format_suspect_details(
        self, suspect: Suspect, evidence: List[Evidence]
    ) -> Message:
        """Форматирует детали подозреваемого в Markdown"""
        text = (
            f"👤 *{suspect.name}*\n\n"
            f"*Описание:* {suspect.description}\n"
            f"*Статус:* {suspect.status.value}\n"
            f"*Уровень риска:* {suspect.risk_level}/10\n"
        )

        if suspect.alibi:
            text += f"\n*Алиби:* {suspect.alibi}"
        if suspect.motive:
            text += f"\n*Мотив:* {suspect.motive}"

        if evidence:
            text += "\n\n*Связанные улики:*\n"
            for ev in evidence:
                text += f"• {ev.name}\n"

        if suspect.notes:
            text += f"\n*Заметки:*\n{suspect.notes}"

        return Message(text=text, parse_mode="Markdown")

    def format_error(self, error: str) -> Message:
        """Форматирует сообщение об ошибке в Markdown"""
        return Message(text=f"❌ *Ошибка*\n\n{error}", parse_mode="Markdown")
