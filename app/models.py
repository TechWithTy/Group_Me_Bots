"""Compatibility layer exposing data models at the top-level ``app`` package."""
from __future__ import annotations

from app.group_me.models import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
