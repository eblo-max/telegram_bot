import pytest
import inspect
from pathlib import Path
from dark_archive.domain.base_classes import BaseEntity
from dark_archive.domain.repositories.base_repository import BaseRepository
from dark_archive.application.use_cases.base_use_case import BaseUseCase
from dark_archive.domain.entities import *
from dark_archive.domain.repositories import *
from dark_archive.application.use_cases import *


def test_domain_layer_independence():
    """Тест независимости доменного слоя."""
    domain_path = Path(__file__).parent.parent.parent / "domain"

    # Проверяем, что в доменном слое нет импортов из других слоев
    for py_file in domain_path.rglob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "from dark_archive.application" not in content
            assert "from dark_archive.infrastructure" not in content
            assert "from dark_archive.interfaces" not in content


def test_entity_base_class():
    """Тест базового класса сущностей."""
    # Проверяем, что все сущности наследуются от BaseEntity
    from dark_archive.domain.entities.player import Player
    from dark_archive.domain.entities.case import Case
    from dark_archive.domain.entities.suspect import Suspect
    from dark_archive.domain.entities.evidence import Evidence
    from dark_archive.domain.entities.location import Location
    from dark_archive.domain.entities.theory import Theory

    entities = [Player, Case, Suspect, Evidence, Location, Theory]
    for entity_class in entities:
        assert issubclass(
            entity_class, BaseEntity
        ), f"{entity_class.__name__} должен наследоваться от BaseEntity"


def test_repository_interfaces():
    """Тест интерфейсов репозиториев."""
    # Проверяем наличие основных методов у всех репозиториев
    required_methods = ["get_by_id", "save", "delete"]

    for name, cls in inspect.getmembers(
        inspect.getmodule(BaseRepository), inspect.isclass
    ):
        if name.endswith("Repository") and name != "BaseRepository":
            for method in required_methods:
                assert hasattr(cls, method)


def test_use_case_structure():
    """Тест структуры use case классов."""
    # Проверяем, что все use case имеют методы execute и execute_sync
    for name, cls in inspect.getmembers(
        inspect.getmodule(BaseUseCase), inspect.isclass
    ):
        if name.endswith("UseCase") and name != "BaseUseCase":
            assert hasattr(cls, "execute")
            assert hasattr(cls, "execute_sync")
