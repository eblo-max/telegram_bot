import logging
import asyncio
from typing import Dict, List
from datetime import datetime, timedelta

from dark_archive.domain.interfaces.lifecycle_manager import ILifecycleManager

logger = logging.getLogger(__name__)


class LifecycleMonitor:
    """Service for monitoring and managing component lifecycles."""

    def __init__(self, check_interval: int = 60):
        self._components: Dict[str, ILifecycleManager] = {}
        self._check_interval = check_interval
        self._last_checks: Dict[str, datetime] = {}
        self._running = False
        self._monitor_task = None

    def register_component(self, name: str, component: ILifecycleManager) -> None:
        """Register a component for monitoring."""
        self._components[name] = component
        self._last_checks[name] = datetime.now()
        logger.info(f"Registered component {name} for lifecycle monitoring")

    def unregister_component(self, name: str) -> None:
        """Unregister a component from monitoring."""
        if name in self._components:
            del self._components[name]
            del self._last_checks[name]
            logger.info(f"Unregistered component {name} from lifecycle monitoring")

    def get_component_status(self, name: str) -> Dict:
        """Get detailed status of a component."""
        if name not in self._components:
            raise ValueError(f"Component {name} not found")

        component = self._components[name]
        last_check = self._last_checks.get(name)

        return {
            "name": name,
            "status": component.status,
            "healthy": component.is_healthy(),
            "last_check": last_check.isoformat() if last_check else None,
            "last_error": str(component.last_error) if component.last_error else None,
        }

    def get_all_statuses(self) -> List[Dict]:
        """Get status of all registered components."""
        return [self.get_component_status(name) for name in self._components]

    async def start_monitoring(self) -> None:
        """Start monitoring components."""
        if self._running:
            logger.warning("Monitoring is already running")
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Started lifecycle monitoring")

    async def stop_monitoring(self) -> None:
        """Stop monitoring components."""
        if not self._running:
            return

        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped lifecycle monitoring")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                await self._check_components()
                await asyncio.sleep(self._check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retrying

    async def _check_components(self) -> None:
        """Check health of all components."""
        now = datetime.now()

        for name, component in self._components.items():
            try:
                if not component.is_healthy():
                    logger.warning(
                        f"Component {name} is unhealthy, attempting recovery"
                    )
                    if component.recover():
                        logger.info(f"Successfully recovered component {name}")
                    else:
                        logger.error(f"Failed to recover component {name}")
                self._last_checks[name] = now
            except Exception as e:
                logger.error(f"Error checking component {name}: {e}")

    async def shutdown(self) -> None:
        """Shutdown all components."""
        await self.stop_monitoring()

        for name, component in self._components.items():
            try:
                component.shutdown()
                logger.info(f"Shutdown component {name}")
            except Exception as e:
                logger.error(f"Error shutting down component {name}: {e}")

    def initialize_all(self) -> bool:
        """Initialize all components."""
        success = True

        for name, component in self._components.items():
            try:
                if not component.initialize():
                    logger.error(f"Failed to initialize component {name}")
                    success = False
            except Exception as e:
                logger.error(f"Error initializing component {name}: {e}")
                success = False

        return success
