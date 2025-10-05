"""Compatibility layer exposing posting helpers at the top level."""
from __future__ import annotations

from app.group_me.posting import *  # noqa: F401,F403

__all__ = [name for name in globals() if not name.startswith("_")]
