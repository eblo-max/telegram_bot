from datetime import datetime, timedelta
from typing import List, Optional

from dark_archive.domain.specifications.specification import Specification
from dark_archive.domain.entities.case import Case


class CaseStatusSpecification(Specification[Case]):
    """Specification for filtering cases by status."""

    def __init__(self, status: str):
        self.status = status

    def is_satisfied_by(self, candidate: Case) -> bool:
        return candidate.status == self.status


class CaseDifficultySpecification(Specification[Case]):
    """Specification for filtering cases by difficulty level."""

    def __init__(
        self, min_difficulty: Optional[int] = None, max_difficulty: Optional[int] = None
    ):
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty

    def is_satisfied_by(self, candidate: Case) -> bool:
        if (
            self.min_difficulty is not None
            and candidate.difficulty < self.min_difficulty
        ):
            return False
        if (
            self.max_difficulty is not None
            and candidate.difficulty > self.max_difficulty
        ):
            return False
        return True


class CaseProgressSpecification(Specification[Case]):
    """Specification for filtering cases by progress."""

    def __init__(self, min_progress: float = 0.0, max_progress: float = 1.0):
        self.min_progress = min_progress
        self.max_progress = max_progress

    def is_satisfied_by(self, candidate: Case) -> bool:
        return self.min_progress <= candidate.progress <= self.max_progress


class CaseAgeSpecification(Specification[Case]):
    """Specification for filtering cases by age."""

    def __init__(self, max_age_days: int):
        self.max_age_days = max_age_days

    def is_satisfied_by(self, candidate: Case) -> bool:
        age = datetime.utcnow() - candidate.created_at
        return age.days <= self.max_age_days


class CaseTagsSpecification(Specification[Case]):
    """Specification for filtering cases by tags."""

    def __init__(self, tags: List[str], match_all: bool = False):
        self.tags = set(tags)
        self.match_all = match_all

    def is_satisfied_by(self, candidate: Case) -> bool:
        case_tags = set(candidate.tags)
        if self.match_all:
            return self.tags.issubset(case_tags)
        return bool(self.tags.intersection(case_tags))


class CaseHasEvidenceSpecification(Specification[Case]):
    """Specification for filtering cases by evidence presence."""

    def __init__(self, evidence_type: Optional[str] = None, min_count: int = 1):
        self.evidence_type = evidence_type
        self.min_count = min_count

    def is_satisfied_by(self, candidate: Case) -> bool:
        if self.evidence_type:
            evidence = [e for e in candidate.evidence if e.type == self.evidence_type]
        else:
            evidence = candidate.evidence
        return len(evidence) >= self.min_count


class CaseHasLocationSpecification(Specification[Case]):
    """Specification for filtering cases by location presence."""

    def __init__(self, location_name: Optional[str] = None):
        self.location_name = location_name

    def is_satisfied_by(self, candidate: Case) -> bool:
        if self.location_name:
            return any(loc.name == self.location_name for loc in candidate.locations)
        return bool(candidate.locations)


class CaseUpdatedRecentlySpecification(Specification[Case]):
    """Specification for filtering cases by recent updates."""

    def __init__(self, hours: int = 24):
        self.hours = hours

    def is_satisfied_by(self, candidate: Case) -> bool:
        if not candidate.updated_at:
            return False
        time_since_update = datetime.utcnow() - candidate.updated_at
        return time_since_update <= timedelta(hours=self.hours)


class CaseNeedsAttentionSpecification(Specification[Case]):
    """Specification for identifying cases that need attention."""

    def __init__(self, inactive_days: int = 7, min_progress: float = 0.0):
        self.inactive_days = inactive_days
        self.min_progress = min_progress

    def is_satisfied_by(self, candidate: Case) -> bool:
        if candidate.status in ["closed", "solved"]:
            return False

        if candidate.progress < self.min_progress:
            return True

        if not candidate.updated_at:
            return True

        time_since_update = datetime.utcnow() - candidate.updated_at
        return time_since_update.days >= self.inactive_days
