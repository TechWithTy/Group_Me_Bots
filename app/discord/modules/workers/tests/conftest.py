"""Reuse root test configuration for worker-level tests."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the shared root configuration for its side effects without
# re-exporting its pytest-specific globals.
importlib.import_module("tests.conftest")

