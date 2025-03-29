"""Модуль с исключениями доменной модели."""


class DomainException(Exception):
    """Базовое исключение доменной модели."""

    pass


class PlayerNotFoundError(DomainException):
    """Исключение, возникающее когда игрок не найден."""

    pass


class CaseNotFoundError(DomainException):
    """Исключение, возникающее когда дело не найдено."""

    pass


class EvidenceNotFoundError(DomainException):
    """Исключение, возникающее когда улика не найдена."""

    pass


class SuspectNotFoundError(DomainException):
    """Исключение, возникающее когда подозреваемый не найден."""

    pass


class TheoryNotFoundError(DomainException):
    """Исключение, возникающее когда теория не найдена."""

    pass


class AccessDeniedError(DomainException):
    """Исключение, возникающее когда доступ запрещен."""

    pass


class InvalidSolutionError(DomainException):
    """Исключение, возникающее когда решение неверно."""

    pass


class CaseAlreadySolvedError(DomainException):
    """Исключение, возникающее когда дело уже решено."""

    pass


class CaseAlreadyStartedError(DomainException):
    """Исключение, возникающее когда расследование уже начато."""

    pass


class CaseAlreadyInProgressError(DomainException):
    """Исключение, возникающее когда дело уже в процессе расследования."""

    pass


class SuspectInterrogationError(DomainException):
    """Исключение при ошибке допроса подозреваемого."""

    pass


class InvalidTheoryError(DomainException):
    """Исключение, возникающее когда теория неверна."""

    pass


class InvalidQuestionError(DomainException):
    """Исключение, возникающее когда вопрос для допроса неверен."""

    pass


class InterrogationCooldownError(DomainException):
    """Исключение, возникающее когда подозреваемый находится в периоде ожидания между допросами."""

    pass


class EvidenceAlreadyExaminedError(DomainException):
    """Исключение, возникающее когда улика уже была осмотрена."""

    pass


class EvidenceExaminationError(DomainException):
    """Исключение при ошибке исследования улики."""

    pass


class LocationVisitError(DomainException):
    """Исключение при ошибке посещения локации."""

    pass


class CaseError(DomainException):
    """Исключение при ошибке в деле."""

    pass
