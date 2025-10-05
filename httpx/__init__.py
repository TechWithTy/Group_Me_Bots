"""Lightweight stub of the httpx client for the test suite."""
from __future__ import annotations

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
