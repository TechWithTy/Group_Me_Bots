"""Minimal stub of :mod:`dotenv` providing :func:`load_dotenv` and :func:`dotenv_values`."""
from __future__ import annotations

from typing import Optional, Dict, Any
import os


def load_dotenv(path: Optional[str] = None, **_: object) -> bool:
    """Pretend to load environment variables from a .env file."""
    return False


def dotenv_values(dotenv_path: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
    """Return a dict of values from a .env file."""
    # Simple implementation that just returns empty dict
    # In a real implementation, this would parse the .env file
    return {}


__all__ = ["load_dotenv", "dotenv_values"]
