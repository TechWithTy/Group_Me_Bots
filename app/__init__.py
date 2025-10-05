"""Top-level package for exposing GroupMe utilities to external consumers."""
from __future__ import annotations

from importlib import import_module
from typing import Any

_GROUP_ME_PACKAGE = import_module("app.group_me")

# Re-export the primary GroupMe entry point for convenience.
GroupMe = _GROUP_ME_PACKAGE.GroupMe

__all__ = ["GroupMe"]


def __getattr__(name: str) -> Any:
    """Defer attribute lookups to the ``app.group_me`` package."""
    return getattr(_GROUP_ME_PACKAGE, name)


def __dir__() -> list[str]:
    """Mirror the attributes provided by ``app.group_me`` for introspection."""
    return sorted(set(__all__) | set(dir(_GROUP_ME_PACKAGE)))
