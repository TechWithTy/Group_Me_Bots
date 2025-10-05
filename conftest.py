"""Expose shared pytest configuration across the repository."""
from __future__ import annotations

from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
_shared_path = ROOT / "tests" / "conftest.py"

if _shared_path.exists():
    namespace = run_path(str(_shared_path))
    globals().update({key: value for key, value in namespace.items() if not key.startswith("__")})
