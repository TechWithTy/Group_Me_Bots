"""Compatibility shim that proxies to ``app.group_me.workflows``."""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

_BASE_PACKAGE = "app.group_me.workflows"
_DELEGATE = import_module(_BASE_PACKAGE)

_package_dir = Path(__file__).resolve().parent
_target_dir = _package_dir.parent / "app" / "group_me" / "workflows"
__path__ = [str(_package_dir), str(_target_dir)]

__all__ = list(getattr(_DELEGATE, "__all__", []))


def __getattr__(name: str) -> Any:
    """Proxy attribute access to the original workflows package."""
    return getattr(_DELEGATE, name)


def __dir__() -> list[str]:
    """Mirror the attributes exposed by the underlying workflows package."""
    return sorted(set(__all__) | set(dir(_DELEGATE)))
