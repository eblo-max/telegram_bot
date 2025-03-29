import pkg_resources
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def check_dependencies() -> None:
    """Проверяет совместимость версий зависимостей"""
    requirements = {
        "anthropic": ">=0.8.1,<0.9.0",
        "python-telegram-bot": "==20.8",
        "dependency-injector": "==4.41.0",
        "python-dotenv": "==1.0.1",
        "openai": "==1.12.0",
        "pydantic": "==2.6.1",
        "httpx": ">=0.26.0",
    }

    for package, version_spec in requirements.items():
        try:
            pkg_resources.require(f"{package}{version_spec}")
        except pkg_resources.VersionConflict as e:
            logger.error(f"Incompatible version of {package}: {e}")
            print(
                f"ERROR: Incompatible version of {package}. Please install {package}{version_spec}"
            )
            raise SystemExit(1)
        except pkg_resources.DistributionNotFound:
            logger.error(f"Package {package} not found")
            print(
                f"ERROR: Package {package} not found. Please install {package}{version_spec}"
            )
            raise SystemExit(1)
