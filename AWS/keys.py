"""Minimal AWS secrets helper used by the tests."""
from __future__ import annotations


def get_secret(name: str) -> str:
    """Return a JSON string representing a fake secret."""

    return "{}"


__all__ = ["get_secret"]
