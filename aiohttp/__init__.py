"""Minimal stub of :mod:`aiohttp` for tests relying on patching."""
from __future__ import annotations

from typing import Any


class ClientSession:
    """Placeholder async client session."""

    async def __aenter__(self) -> "ClientSession":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def post(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("aiohttp stub does not implement network calls")


__all__ = ["ClientSession"]
