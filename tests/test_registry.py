"""Guard: every tool defined in the package is exported from the package.

A tool class that exists in a platform module but never reaches ``__init__``
is invisible to users, and that has happened twice in this codebase. These
tests fail loudly on the next occurrence.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import crewai_scavio
from crewai_scavio._base import ScavioBaseTool

# One tool per billable endpoint the API exposes.
EXPECTED_TOOL_COUNT = 97


def _tool_classes_in_modules() -> dict[str, type]:
    """Collect every ScavioBaseTool subclass defined in the platform modules."""
    found: dict[str, type] = {}
    for mod_info in pkgutil.iter_modules(crewai_scavio.__path__):
        module = importlib.import_module(f"crewai_scavio.{mod_info.name}")
        for name, obj in vars(module).items():
            if (
                inspect.isclass(obj)
                and issubclass(obj, ScavioBaseTool)
                and obj is not ScavioBaseTool
                and obj.__module__ == module.__name__
            ):
                found[name] = obj
    return found


def test_every_tool_is_exported():
    """Every tool class defined in a module is importable from the package."""
    exported = set(crewai_scavio.__all__)
    defined = set(_tool_classes_in_modules())
    assert defined - exported == set()


def test_all_entries_resolve():
    """Every name in __all__ actually exists on the package."""
    for name in crewai_scavio.__all__:
        assert hasattr(crewai_scavio, name), name


def test_no_duplicate_exports():
    """__all__ has no repeated entries."""
    assert len(crewai_scavio.__all__) == len(set(crewai_scavio.__all__))


def test_tool_count_matches_endpoint_count():
    """The package exposes one tool per billable endpoint."""
    assert len(crewai_scavio.__all__) == EXPECTED_TOOL_COUNT
    assert len(_tool_classes_in_modules()) == EXPECTED_TOOL_COUNT


def test_tool_names_are_unique():
    """No two tools share a display name, which would confuse an agent."""
    names = [
        getattr(crewai_scavio, n).model_fields["name"].default
        for n in crewai_scavio.__all__
    ]
    assert len(names) == len(set(names))
