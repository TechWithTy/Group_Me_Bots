"""Pytest configuration for path setup and third-party stubs."""
from __future__ import annotations

import sys
from pathlib import Path

module = sys.modules.get("httpx")
if module is not None and not hasattr(module, "Response"):  # pragma: no cover - replace stub
    sys.modules.pop("httpx", None)

try:  # pragma: no cover - import guard for optional dependency
    import httpx  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - fallback stub
    from typing import Any

    class _HttpxStub:
        class AsyncClient:  # type: ignore[too-few-public-methods]
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self._kwargs = kwargs

            async def get(self, *args: Any, **kwargs: Any) -> None:
                raise RuntimeError("httpx.AsyncClient.get not stubbed")

            async def post(self, *args: Any, **kwargs: Any) -> None:
                raise RuntimeError("httpx.AsyncClient.post not stubbed")

            async def aclose(self) -> None:
                return None

    sys.modules.setdefault("httpx", _HttpxStub())

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
