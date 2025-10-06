"""Utility helpers shared across the state management modules."""

from __future__ import annotations

import base64
import time


def now_ms() -> int:
    """Return a monotonically increasing millisecond timestamp."""

    return int(time.time() * 1000)


def placeholder_image(seed: str) -> str:
    """Return a deterministic base64 placeholder image string."""

    encoded = base64.b64encode(seed.encode("utf-8")).decode("ascii")
    return f"data:image/png;base64,{encoded}"

