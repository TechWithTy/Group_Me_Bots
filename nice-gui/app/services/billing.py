"""Checkout orchestration for purchasing add-on credits."""

from __future__ import annotations

from typing import Callable, Dict
from uuid import uuid4


class CheckoutService:
    """Simulate checkout sessions and credit allocation."""

    def __init__(self, on_change: Callable[[int], None], log: Callable[[str], None]) -> None:
        self._on_change = on_change
        self._log = log
        self._sessions: Dict[str, int] = {}
        self.addon_credits = 0

    def create_session(self, credit_amount: int) -> tuple[str, str]:
        """Create a demo checkout session and return its metadata."""

        session_id = f"session_{uuid4().hex[:8]}"
        self._sessions[session_id] = credit_amount
        self._log(f"Checkout started for {credit_amount} credits")
        return session_id, f"https://payments.example.com/checkout/{session_id}"

    def complete(self, session_id: str) -> int:
        """Finalize a checkout session and apply the credit package."""

        amount = self._sessions.pop(session_id, None)
        if amount is None:
            raise ValueError("Unknown checkout session")
        self.addon_credits += amount
        self._log(f"Payment confirmed for {amount} credits")
        self._on_change(self.addon_credits)
        return amount
