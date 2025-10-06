"""Compatibility namespace to satisfy legacy imports within tests."""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

_BASE_PACKAGE = "app.group_me.workers"
_DELEGATE = import_module(_BASE_PACKAGE)

_package_dir = Path(__file__).resolve().parent
_parent_dir = _package_dir.parent
__path__ = [str(_package_dir), str(_parent_dir)]

__all__ = list(getattr(_DELEGATE, "__all__", []))


def __getattr__(name: str) -> Any:
    return getattr(_DELEGATE, name)


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(dir(_DELEGATE)))
