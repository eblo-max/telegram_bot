from datetime import datetime, timedelta
from typing import Optional, List

from dark_archive.domain.specifications.specification import Specification
from dark_archive.domain.value_objects.location import Location


class LocationTypeSpecification(Specification[Location]):
    """Specification for filtering locations by type."""

    def __init__(self, location_type: str):
        self.location_type = location_type

    def is_satisfied_by(self, candidate: Location) -> bool:
        return candidate.type == self.location_type


class LocationHasEvidenceSpecification(Specification[Location]):
    """Specification for filtering locations by evidence presence."""

    def __init__(self, min_evidence: int = 1):
        self.min_evidence = min_evidence

    def is_satisfied_by(self, candidate: Location) -> bool:
        return len(candidate.evidence_ids) >= self.min_evidence


class LocationHasDescriptionSpecification(Specification[Location]):
    """Specification for filtering locations by description presence."""

    def __init__(self, min_length: Optional[int] = None):
        self.min_length = min_length

    def is_satisfied_by(self, candidate: Location) -> bool:
        if not candidate.description:
            return False
        if self.min_length:
            return len(candidate.description) >= self.min_length
        return True


class LocationHasCoordinatesSpecification(Specification[Location]):
    """Specification for filtering locations by coordinates presence."""

    def is_satisfied_by(self, candidate: Location) -> bool:
        return candidate.coordinates is not None


class LocationIsAccessibleSpecification(Specification[Location]):
    """Specification for filtering accessible locations."""

    def is_satisfied_by(self, candidate: Location) -> bool:
        return candidate.is_accessible


class LocationHasHintsSpecification(Specification[Location]):
    """Specification for filtering locations by hints presence."""

    def __init__(self, min_hints: int = 1):
        self.min_hints = min_hints

    def is_satisfied_by(self, candidate: Location) -> bool:
        return len(candidate.hints) >= self.min_hints


class LocationNeedsInvestigationSpecification(Specification[Location]):
    """Specification for identifying locations that need investigation."""

    def __init__(self, min_evidence_threshold: int = 3):
        self.min_evidence_threshold = min_evidence_threshold

    def is_satisfied_by(self, candidate: Location) -> bool:
        # Локация требует расследования если:
        # 1. Она доступна
        # 2. Имеет описание
        # 3. Имеет мало улик
        return (
            candidate.is_accessible
            and bool(candidate.description)
            and len(candidate.evidence_ids) < self.min_evidence_threshold
        )


class LocationIsSignificantSpecification(Specification[Location]):
    """Specification for identifying significant locations."""

    def __init__(self, min_evidence: int = 3, min_description_length: int = 100):
        self.min_evidence = min_evidence
        self.min_description_length = min_description_length

    def is_satisfied_by(self, candidate: Location) -> bool:
        # Локация считается значимой если:
        # 1. Имеет достаточное количество улик
        # 2. Имеет подробное описание
        # 3. Имеет координаты
        # 4. Имеет хотя бы одну подсказку
        return (
            len(candidate.evidence_ids) >= self.min_evidence
            and len(candidate.description) >= self.min_description_length
            and candidate.coordinates is not None
            and len(candidate.hints) > 0
        )
