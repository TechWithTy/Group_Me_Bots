"""Minimal stub of :mod:`dotenv` providing :func:`load_dotenv`."""
from __future__ import annotations

from typing import Optional


def load_dotenv(path: Optional[str] = None, **_: object) -> bool:
    """Pretend to load environment variables from a .env file."""

    return False


__all__ = ["load_dotenv"]
