from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar("T")


class Specification(Generic[T], ABC):
    """Base interface for specifications."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies the specification."""
        pass

    def and_(self, other: "Specification[T]") -> "AndSpecification[T]":
        """Combine with another specification using AND."""
        return AndSpecification(self, other)

    def or_(self, other: "Specification[T]") -> "OrSpecification[T]":
        """Combine with another specification using OR."""
        return OrSpecification(self, other)

    def not_(self) -> "NotSpecification[T]":
        """Negate this specification."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """Specification that combines two specifications with AND."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(
            candidate
        )


class OrSpecification(Specification[T]):
    """Specification that combines two specifications with OR."""

    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(
            candidate
        )


class NotSpecification(Specification[T]):
    """Specification that negates another specification."""

    def __init__(self, spec: Specification[T]):
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)


class CompositeSpecification(Specification[T]):
    """Base class for specifications that can be combined."""

    def __init__(self, specs: List[Specification[T]]):
        self.specs = specs

    def add(self, spec: Specification[T]) -> None:
        """Add a specification to the composite."""
        self.specs.append(spec)

    def remove(self, spec: Specification[T]) -> None:
        """Remove a specification from the composite."""
        self.specs.remove(spec)


class AllSpecification(CompositeSpecification[T]):
    """Specification that requires all child specifications to be satisfied."""

    def is_satisfied_by(self, candidate: T) -> bool:
        return all(spec.is_satisfied_by(candidate) for spec in self.specs)


class AnySpecification(CompositeSpecification[T]):
    """Specification that requires any child specification to be satisfied."""

    def is_satisfied_by(self, candidate: T) -> bool:
        return any(spec.is_satisfied_by(candidate) for spec in self.specs)
