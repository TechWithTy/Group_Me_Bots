"""Lightweight stub of the ``requests`` library for offline unit tests."""
from __future__ import annotations

from typing import Any, Callable


class RequestException(Exception):
    """Base exception matching the public ``requests`` API."""


class _ExceptionsModule:
    RequestException = RequestException


exceptions = _ExceptionsModule()


def _raise(*args: Any, **kwargs: Any) -> None:
    raise RequestException("requests library is not available in this environment")


get: Callable[..., Any] = _raise
post: Callable[..., Any] = _raise

__all__ = ["RequestException", "exceptions", "get", "post"]
