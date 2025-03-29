from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

from dark_archive.domain.validation.validator import Validator


class EvidenceValidator(Validator):
    """Validator for Evidence value object."""

    def _validate(self, evidence: "Evidence") -> None:
        """Validate evidence data."""
        self.validate_string(evidence.description, "description", min_length=10)
        self.validate_string(
            evidence.type, "type", pattern=r"^(photo|video|audio|text|physical|other)$"
        )

        if evidence.metadata:
            self.validate_dict(evidence.metadata, "metadata")

        if evidence.analysis:
            self.validate_string(evidence.analysis, "analysis", min_length=10)

        if evidence.source:
            self.validate_string(evidence.source, "source", min_length=2)


@dataclass
class Evidence:
    """Represents a piece of evidence in a paranormal investigation."""

    description: str
    type: str = "other"
    metadata: Optional[Dict[str, Any]] = None
    analysis: Optional[str] = None
    source: Optional[str] = None
    collected_at: datetime = datetime.utcnow()

    def __post_init__(self):
        self._validator = EvidenceValidator()
        self.validate()

    def validate(self) -> None:
        """Validate evidence data."""
        if self._validator:
            self._validator.validate(self)

    def add_analysis(self, analysis: str) -> None:
        """Add analysis to the evidence."""
        self.analysis = analysis
        self.validate()

    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update evidence metadata."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata.update(metadata)
        self.validate()

    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to dictionary."""
        return {
            "description": self.description,
            "type": self.type,
            "metadata": self.metadata,
            "analysis": self.analysis,
            "source": self.source,
            "collected_at": self.collected_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evidence":
        """Create evidence from dictionary data."""
        if "collected_at" in data:
            data["collected_at"] = datetime.fromisoformat(data["collected_at"])
        return cls(**data)
