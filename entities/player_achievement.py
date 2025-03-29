from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID


@dataclass
class PlayerAchievement:
    """Represents an achievement earned by a player."""

    player_id: UUID
    achievement_id: UUID
    earned_at: datetime
    progress: float = 0.0  # Progress towards achievement (0.0 - 1.0)
    completed: bool = False
    metadata: Optional[Dict] = None  # Additional data about achievement progress

    def __post_init__(self):
        """Validate player achievement data after initialization."""
        if self.progress < 0.0 or self.progress > 1.0:
            raise ValueError("Achievement progress must be between 0.0 and 1.0")
        if self.completed and self.progress < 1.0:
            raise ValueError("Completed achievements must have 100% progress")

    def update_progress(self, new_progress: float) -> None:
        """Update achievement progress."""
        if new_progress < 0.0 or new_progress > 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        self.progress = new_progress
        if new_progress >= 1.0:
            self.complete()

    def complete(self) -> None:
        """Mark achievement as completed."""
        self.progress = 1.0
        self.completed = True

    def to_dict(self) -> Dict:
        """Convert player achievement to dictionary representation."""
        return {
            "player_id": str(self.player_id),
            "achievement_id": str(self.achievement_id),
            "earned_at": self.earned_at.isoformat(),
            "progress": self.progress,
            "completed": self.completed,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PlayerAchievement":
        """Create player achievement instance from dictionary data."""
        return cls(
            player_id=UUID(data["player_id"]),
            achievement_id=UUID(data["achievement_id"]),
            earned_at=datetime.fromisoformat(data["earned_at"]),
            progress=data["progress"],
            completed=data["completed"],
            metadata=data.get("metadata"),
        )
