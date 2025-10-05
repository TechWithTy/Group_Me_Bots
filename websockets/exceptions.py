"""Exception definitions for the websockets stub."""
from __future__ import annotations


class ConnectionClosed(Exception):
    """Exception representing a closed websocket."""


__all__ = ["ConnectionClosed"]
