from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ILifecycleManager(ABC):
    """Interface for managing component lifecycle."""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the component.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Gracefully shutdown the component."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if the component is healthy and functioning properly.

        Returns:
            bool: True if the component is healthy, False otherwise.
        """
        pass

    @abstractmethod
    def recover(self) -> bool:
        """Attempt to recover the component from an unhealthy state.

        Returns:
            bool: True if recovery was successful, False otherwise.
        """
        pass

    @property
    @abstractmethod
    def status(self) -> str:
        """Get the current status of the component.

        Returns:
            str: Current status (e.g., "initialized", "running", "stopped", "error").
        """
        pass

    @property
    @abstractmethod
    def last_error(self) -> Optional[Exception]:
        """Get the last error that occurred.

        Returns:
            Optional[Exception]: The last error or None if no error occurred.
        """
        pass
