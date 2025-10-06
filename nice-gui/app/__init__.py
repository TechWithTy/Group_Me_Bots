"""Application bootstrap for the NiceGUI operations dashboard."""

from __future__ import annotations

import sys
from pathlib import Path


# Ensure the repository root is importable so Pydantic schemas are available.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from .pages.dashboard import render_dashboard


def build() -> None:
    """Construct the NiceGUI interface."""
    print('Building dashboard...')
    render_dashboard()
    print('Dashboard built successfully')
