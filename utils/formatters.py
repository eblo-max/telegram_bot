# Created by setup script

from dark_archive.domain.entities.case import Case
from dark_archive.domain.entities.evidence import Evidence
from dark_archive.domain.entities.suspect import Suspect
from typing import List
from datetime import datetime


def format_case_details(case: Case) -> str:
    """Форматирует детали дела для отображения в Telegram"""
    if not case:
        return "Дело не найдено"

    evidence_text = format_evidence_list(case.evidences)
    suspects_text = format_suspects_list(case.suspects)
    notes_text = format_notes_list(case.notes)

    return (
        f"<b>📂 Дело #{case.id}</b>\n"
        f"\n"
        f"<b>Название:</b> {case.title}\n"
        f"\n"
        f"<b>Описание:</b>\n"
        f"{case.description}\n"
        f"\n"
        f"<b>🔍 Улики ({len(case.evidences)}):</b>\n"
        f"{evidence_text}\n"
        f"\n"
        f"<b>👥 Подозреваемые ({len(case.suspects)}):</b>\n"
        f"{suspects_text}\n"
        f"\n"
        f"<b>📝 Заметки детектива:</b>\n"
        f"{notes_text}\n"
        f"\n"
        f"<b>Статус:</b> {'🟢 Открыто' if case.status == 'active' else '🔴 Закрыто'}\n"
        f"<b>Создано:</b> {format_datetime(case.created_at)}\n"
        f"<b>Обновлено:</b> {format_datetime(case.updated_at)}"
    )


def format_evidence_list(evidence: List[Evidence]) -> str:
    """Форматирует список улик"""
    if not evidence:
        return "Улики не найдены"
    return "".join([f"• {e.title}: {e.description} ({e.type})\n" for e in evidence])


def format_suspects_list(suspects: List[Suspect]) -> str:
    """Форматирует список подозреваемых"""
    if not suspects:
        return "Подозреваемые не установлены"
    return "".join(
        [f"• {s.name}: {s.description} (Статус: {s.status})\n" for s in suspects]
    )


def format_notes_list(notes: List[str]) -> str:
    """Форматирует список заметок"""
    if not notes:
        return "Заметок нет"
    return "".join([f"• {note}\n" for note in notes])


def format_datetime(dt: datetime) -> str:
    """Форматирует дату и время"""
    return dt.strftime("%d.%m.%Y %H:%M")
