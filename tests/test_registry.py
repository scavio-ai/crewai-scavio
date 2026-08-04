"""Guard: every tool defined in the package is exported from the package.

A tool class that exists in a platform module but never reaches ``__init__``
is invisible to users, and that has happened twice in this codebase. These
tests fail loudly on the next occurrence.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

from scavio._spec import ENDPOINTS

import crewai_scavio
from crewai_scavio._base import ScavioBaseTool

# Endpoints no integration package wraps: retired paths, deprecated aliases and
# unbilled GET helpers. Mirrors EXCLUDED in integrations/coverage-check.py.
EXCLUDED_ENDPOINTS = frozenset(
    {
        "/api/v1/google",  # retired 2026-08-04, returns 410
        "/api/v1/youtube/metadata",  # deprecated alias of /youtube/video
        "/api/v1/linkedin/person/contact",  # retired upstream, 410 unbilled
        "/api/v1/linkedin/company/people",
        "/api/v1/linkedin/company/jobs",
        "/api/v1/linkedin/search/people",
        "/api/v1/linkedin/search/posts",
        "/api/v1/amazon/options",  # GET metadata helper, unbilled
        "/api/v1/usage",  # GET account helper, unbilled
    }
)


def _billable_endpoint_count() -> int:
    """Count billable endpoints in the SDK spec, the one source of truth.

    Derived rather than hardcoded so that adding endpoint 98 upstream fails
    this suite instead of passing green against a stale literal.
    """
    paths = {endpoint.path for endpoint in ENDPOINTS.values()}
    return len(paths - EXCLUDED_ENDPOINTS)


# One tool per billable endpoint the API exposes.
EXPECTED_TOOL_COUNT = _billable_endpoint_count()


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


def test_excluded_endpoints_are_all_real_spec_paths_or_gone():
    """Guard the exclusion list itself against drifting into fiction.

    An entry that is neither in the spec nor a known retired path means the
    list has gone stale and is silently shrinking the expected count.
    """
    known_gone = {
        "/api/v1/google",
        "/api/v1/youtube/metadata",
        "/api/v1/usage",
    }
    paths = {endpoint.path for endpoint in ENDPOINTS.values()}
    for excluded in EXCLUDED_ENDPOINTS:
        assert excluded in paths or excluded in known_gone, excluded


def test_tool_names_are_unique():
    """No two tools share a display name, which would confuse an agent."""
    names = [
        getattr(crewai_scavio, n).model_fields["name"].default
        for n in crewai_scavio.__all__
    ]
    assert len(names) == len(set(names))
