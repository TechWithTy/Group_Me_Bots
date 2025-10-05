"""Minimal stub of :mod:`websockets` for offline tests."""
from __future__ import annotations

from typing import Any

from .exceptions import ConnectionClosed


class WebSocketServerProtocol:
    """Placeholder websocket protocol."""

    async def send(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError

    async def recv(self) -> Any:
        raise NotImplementedError


__all__ = ["WebSocketServerProtocol", "ConnectionClosed"]
