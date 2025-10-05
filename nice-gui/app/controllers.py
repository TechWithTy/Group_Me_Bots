"""Controllers that encapsulate automation logic."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, List, MutableMapping, Sequence

from _schema.schemas.bots import ChatBot


class BotController:
    """Track bot activation state and notify observers."""

    def __init__(self, bots: Sequence[ChatBot]) -> None:
        self._status: Dict[str, bool] = {
            bot.bot_name: bool(bot.is_active) for bot in bots
        }
        self._status_listeners: MutableMapping[str, List[Callable[[bool], None]]] = defaultdict(list)
        self._log_listeners: List[Callable[[str], None]] = []

    def subscribe_status(self, bot_name: str, callback: Callable[[bool], None]) -> None:
        """Register a callback for status changes of ``bot_name``."""

        self._status_listeners[bot_name].append(callback)

    def subscribe_log(self, callback: Callable[[str], None]) -> None:
        """Register a callback for automation activity log events."""

        self._log_listeners.append(callback)

    def set_status(self, bot_name: str, active: bool) -> None:
        """Update a bot status and notify listeners when it changes."""

        if self._status[bot_name] == active:
            return
        self._status[bot_name] = active
        for callback in self._status_listeners[bot_name]:
            callback(active)
        event = f"{bot_name} automation {'activated' if active else 'paused'}"
        for callback in self._log_listeners:
            callback(event)

    def get_status(self, bot_name: str) -> bool:
        """Return the activation state for ``bot_name``."""

        return self._status[bot_name]

    def count_active(self) -> int:
        """Return the number of bots that are currently active."""

        return sum(1 for value in self._status.values() if value)

    def total(self) -> int:
        """Return the total number of tracked bots."""

        return len(self._status)
