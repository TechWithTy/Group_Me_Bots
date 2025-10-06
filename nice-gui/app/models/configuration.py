"""Configuration section models for dashboard metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple


@dataclass(frozen=True)
class ConfigurationSection:
    """Structured configuration data displayed in the dashboard."""

    title: str
    items: Sequence[Tuple[str, str]]
    description: str | None = None
