"""Lightweight stub of the httpx client for the test suite."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path


def _load_real_httpx():
    module_name = __name__
    package_parent = Path(__file__).resolve().parent

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
            if Path(entry).resolve() != package_parent.parent.resolve()
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


_REAL_MODULE = _load_real_httpx()

if _REAL_MODULE is not None:
    __all__ = getattr(_REAL_MODULE, "__all__", [])

    def __getattr__(name: str):  # type: ignore[override]
        return getattr(_REAL_MODULE, name)

else:

    from typing import Any

    class AsyncClient:  # type: ignore[too-few-public-methods]
        """Stub async client mirroring the httpx.AsyncClient interface."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self._kwargs = kwargs

        async def get(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("httpx.AsyncClient.get not stubbed")

        async def post(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("httpx.AsyncClient.post not stubbed")

        async def aclose(self) -> None:
            return None

    __all__ = ["AsyncClient"]
