"""Test fixtures for the NiceGUI dashboard simulator."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

# Ensure the repository root is importable for the simulator dependencies.
ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "nice-gui"
for path in (ROOT, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from nicegui.testing import User


@pytest.fixture
def user() -> User:
    """Provide a simulated NiceGUI user for integration tests."""

    return User()
