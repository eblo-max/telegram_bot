from enum import Enum


class PlayerRole(Enum):
    """Роли игроков в системе."""

    DETECTIVE = "detective"
    ADMIN = "admin"
    OBSERVER = "observer"


class CaseStatus(Enum):
    """Статусы дел."""

    NEW = "new"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    SOLVED = "solved"
    CLOSED = "closed"


class EvidenceType(Enum):
    """Типы улик."""

    PHYSICAL = "physical"
    DOCUMENTARY = "documentary"
    WITNESS = "witness"
    DIGITAL = "digital"
    FORENSIC = "forensic"


class SuspectStatus(Enum):
    """Статусы подозреваемых."""

    NOT_INTERROGATED = "not_interrogated"
    INTERROGATED = "interrogated"
    IN_COOLDOWN = "in_cooldown"
    CLEARED = "cleared"
    GUILTY = "guilty"


class CaseDifficulty(Enum):
    """Сложность дела"""

    EASY = "easy"  # Легкое
    MEDIUM = "medium"  # Среднее
    HARD = "hard"  # Сложное


class InterrogationState(Enum):
    """Состояния допроса"""

    COOPERATIVE = "cooperative"  # Сотрудничает
    UNCOOPERATIVE = "uncooperative"  # Не сотрудничает
    HOSTILE = "hostile"  # Враждебно настроен
    SILENT = "silent"  # Молчит
