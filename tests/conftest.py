"""Pytest configuration for path setup and third-party stubs."""
from __future__ import annotations

import builtins
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
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

os.environ.setdefault("DISCORD_BOT_TOKEN", "test-token")

if "discord" not in sys.modules:
    discord_stub = ModuleType("discord")

    class _DummyChannelType(SimpleNamespace):
        news = "news"

    class _DummyIntents:
        @staticmethod
        def all() -> str:
            return "all"

    class _DummyTree(SimpleNamespace):
        def __init__(self) -> None:
            super().__init__(
                command=lambda **_: (lambda func: func),
                remove_command=lambda *_: None,
                clear=lambda: None,
                sync=AsyncMock(),
            )

    class _DummyBot:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.user = SimpleNamespace(
                id=0,
                name="stub",
                discriminator="0000",
                bot=True,
            )
            self.guilds = []
            self.private_channels = []
            self.tree = _DummyTree()

        async def wait_until_ready(self) -> None:
            return None

        def is_ready(self) -> bool:
            return True

        async def start(self, *_: Any, **__: Any) -> None:
            return None

        def event(self, func):
            return func

    commands_module = ModuleType("discord.ext.commands")
    commands_module.Bot = _DummyBot  # type: ignore[attr-defined]

    discord_stub.Intents = _DummyIntents
    discord_stub.ChannelType = _DummyChannelType
    discord_stub.NotFound = Exception
    discord_stub.LoginFailure = Exception
    discord_stub.Object = lambda *, id: SimpleNamespace(id=id)
    ext_module = ModuleType("discord.ext")
    ext_module.commands = commands_module  # type: ignore[attr-defined]

    sys.modules.setdefault("discord", discord_stub)
    sys.modules.setdefault("discord.ext", ext_module)
    sys.modules.setdefault("discord.ext.commands", commands_module)

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
