"""Compatibility shim that proxies to ``app.group_me.workers``."""
from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

_BASE_PACKAGE = "app.group_me.workers"
_DELEGATE = import_module(_BASE_PACKAGE)

# Ensure submodules from the original package are discoverable via this shim.
_package_dir = Path(__file__).resolve().parent
_target_dir = _package_dir.parent / "app" / "group_me" / "workers"
__path__ = [str(_package_dir), str(_target_dir)]

__all__ = list(getattr(_DELEGATE, "__all__", []))


def __getattr__(name: str) -> Any:
    """Proxy attribute access to the original workers package."""
    return getattr(_DELEGATE, name)


def __dir__() -> list[str]:
    """Mirror the attributes exposed by the underlying workers package."""
    return sorted(set(__all__) | set(dir(_DELEGATE)))
