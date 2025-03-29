from datetime import datetime, timedelta
from typing import Optional, List

from dark_archive.domain.specifications.specification import Specification
from dark_archive.domain.value_objects.evidence import Evidence


class EvidenceTypeSpecification(Specification[Evidence]):
    """Specification for filtering evidence by type."""

    def __init__(self, evidence_type: str):
        self.evidence_type = evidence_type

    def is_satisfied_by(self, candidate: Evidence) -> bool:
        return candidate.type == self.evidence_type


class EvidenceHasAnalysisSpecification(Specification[Evidence]):
    """Specification for filtering evidence by analysis presence."""

    def __init__(self, min_length: Optional[int] = None):
        self.min_length = min_length

    def is_satisfied_by(self, candidate: Evidence) -> bool:
        if not candidate.analysis:
            return False
        if self.min_length:
            return len(candidate.analysis) >= self.min_length
        return True


class EvidenceSourceSpecification(Specification[Evidence]):
    """Specification for filtering evidence by source."""

    def __init__(self, source: str):
        self.source = source

    def is_satisfied_by(self, candidate: Evidence) -> bool:
        return candidate.source == self.source


class EvidenceCollectedRecentlySpecification(Specification[Evidence]):
    """Specification for filtering evidence by collection time."""

    def __init__(self, hours: int = 24):
        self.hours = hours

    def is_satisfied_by(self, candidate: Evidence) -> bool:
        time_since_collection = datetime.utcnow() - candidate.collected_at
        return time_since_collection <= timedelta(hours=self.hours)


class EvidenceHasMetadataSpecification(Specification[Evidence]):
    """Specification for filtering evidence by metadata presence."""

    def __init__(self, required_keys: Optional[List[str]] = None):
        self.required_keys = set(required_keys) if required_keys else None

    def is_satisfied_by(self, candidate: Evidence) -> bool:
        if not candidate.metadata:
            return False
        if self.required_keys:
            return self.required_keys.issubset(candidate.metadata.keys())
        return True


class EvidenceNeedsAnalysisSpecification(Specification[Evidence]):
    """Specification for identifying evidence that needs analysis."""

    def is_satisfied_by(self, candidate: Evidence) -> bool:
        return not bool(candidate.analysis)


class EvidenceIsSignificantSpecification(Specification[Evidence]):
    """Specification for identifying significant evidence."""

    def __init__(self, min_analysis_length: int = 100):
        self.min_analysis_length = min_analysis_length

    def is_satisfied_by(self, candidate: Evidence) -> bool:
        if not candidate.analysis:
            return False

        # Проверяем длину анализа
        if len(candidate.analysis) < self.min_analysis_length:
            return False

        # Проверяем наличие метаданных
        if not candidate.metadata:
            return False

        # Проверяем тип улики (фото, видео и аудио считаются более значимыми)
        return candidate.type in ["photo", "video", "audio"]
