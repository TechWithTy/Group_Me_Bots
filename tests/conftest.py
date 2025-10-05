"""Pytest configuration for path setup and third-party stubs."""
from __future__ import annotations

import builtins
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
import datetime as _datetime

pytest_plugins = ["pytest_asyncio"]

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

module = sys.modules.get("httpx")
if module is not None and not hasattr(module, "Response"):  # pragma: no cover - replace stub
    sys.modules.pop("httpx", None)

try:  # pragma: no cover - import guard for optional dependency
    import httpx  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - fallback stub
    from types import ModuleType

    httpx_stub = ModuleType("httpx")

    class AsyncClient:  # type: ignore[too-few-public-methods]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self._kwargs = kwargs

        async def get(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("httpx.AsyncClient.get not stubbed")

        async def post(self, *args: Any, **kwargs: Any) -> None:
            raise RuntimeError("httpx.AsyncClient.post not stubbed")

        async def aclose(self) -> None:
            return None

    httpx_stub.AsyncClient = AsyncClient  # type: ignore[attr-defined]
    sys.modules.setdefault("httpx", httpx_stub)

from app.posting import send_message_to_groups

os.environ.setdefault("ZB_PROMO", "test-access-token")
builtins.send_message_to_groups = send_message_to_groups

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if not hasattr(_datetime, "utcnow"):
    _datetime.utcnow = _datetime.datetime.utcnow  # type: ignore[attr-defined]


@pytest.fixture
def mock_groupme_client() -> MagicMock:
    """Provide a fully stubbed GroupMe client for worker tests."""

    client: MagicMock = MagicMock()
    client.tenant_id = "test-tenant"
    client.groups = SimpleNamespace(
        get=AsyncMock(return_value={}),
        add_members=AsyncMock(return_value={}),
        list=AsyncMock(return_value=[]),
    )
    client.messages = SimpleNamespace(
        post_to_group=AsyncMock(return_value={}),
        like_message=AsyncMock(return_value={}),
        get_message=AsyncMock(return_value={}),
    )
    client.bots = SimpleNamespace(
        create=AsyncMock(return_value={}),
        list=AsyncMock(return_value=[]),
        post=AsyncMock(return_value={}),
        destroy=AsyncMock(return_value={}),
    )

    return client


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Provide a lightweight database session stub."""

    return MagicMock()
