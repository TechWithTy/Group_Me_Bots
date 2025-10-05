"""Entry point for the modular operations dashboard."""

from __future__ import annotations

from pathlib import Path
import sys

from nicegui import ui

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from app import build


ui.run(build)
