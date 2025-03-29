from dataclasses import dataclass
from typing import Dict, Any, Optional

from dark_archive.domain.validation.validator import Validator


class LocationValidator(Validator):
    """Validator for Location value object."""

    def _validate(self, location: "Location") -> None:
        """Validate location data."""
        self.validate_string(location.name, "name", min_length=2, max_length=100)
        self.validate_string(location.description, "description", min_length=10)

        if location.coordinates:
            self.validate_dict(
                location.coordinates,
                "coordinates",
                required_keys=["latitude", "longitude"],
                value_type=float,
            )

            lat = location.coordinates.get("latitude")
            lon = location.coordinates.get("longitude")

            if lat is not None:
                self.validate_number(
                    lat, "coordinates.latitude", min_value=-90, max_value=90
                )
            if lon is not None:
                self.validate_number(
                    lon, "coordinates.longitude", min_value=-180, max_value=180
                )


@dataclass
class Location:
    """Represents a location where paranormal activity was observed."""

    name: str
    description: str
    coordinates: Optional[Dict[str, float]] = None

    def __post_init__(self):
        self._validator = LocationValidator()
        self.validate()

    def validate(self) -> None:
        """Validate location data."""
        if self._validator:
            self._validator.validate(self)

    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "coordinates": self.coordinates,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Location":
        """Create location from dictionary data."""
        return cls(
            name=data["name"],
            description=data["description"],
            coordinates=data.get("coordinates"),
        )
