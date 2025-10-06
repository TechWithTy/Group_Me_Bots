"""Minimal stub of :mod:`websockets` with passthrough to the real package."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

from .exceptions import ConnectionClosed


def _load_real_websockets():
    """Load the external :mod:`websockets` distribution when it is installed."""

    module_name = __name__
    package_parent = Path(__file__).resolve().parent.parent

    submodule_prefix = f"{module_name}."
    cached_modules = {
        name: sys.modules[name]
        for name in list(sys.modules)
        if name == module_name or name.startswith(submodule_prefix)
    }
    original_sys_path = list(sys.path)

    try:
        for name in cached_modules:
            sys.modules.pop(name, None)

        sys.path = [
            entry
            for entry in original_sys_path
            if Path(entry).resolve() != package_parent.resolve()
        ]

        module = importlib.import_module(module_name)
    except Exception:  # pragma: no cover - falls back to stub
        sys.modules.update(cached_modules)
        return None
    else:
        sys.modules[module_name] = module
        return module
    finally:
        sys.path = original_sys_path


_REAL_MODULE = _load_real_websockets()

if _REAL_MODULE is not None:
    __all__ = getattr(_REAL_MODULE, "__all__", [])

    def __getattr__(name: str) -> Any:
        return getattr(_REAL_MODULE, name)

    ConnectionClosed = getattr(_REAL_MODULE, "ConnectionClosed", ConnectionClosed)

else:

    class WebSocketServerProtocol:
        """Placeholder websocket protocol."""

        async def send(self, *args: Any, **kwargs: Any) -> None:
            raise NotImplementedError

        async def recv(self) -> Any:
            raise NotImplementedError

    __all__ = ["WebSocketServerProtocol", "ConnectionClosed"]
