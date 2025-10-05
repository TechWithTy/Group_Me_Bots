"""Compatibility wrapper exposing GroupMe migration utilities."""
from __future__ import annotations

from app.group_me.migration import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
