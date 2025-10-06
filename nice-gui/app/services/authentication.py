"""Authentication orchestration for the operations dashboard."""

from __future__ import annotations

from typing import Callable, List, Optional
from uuid import uuid4

from ..models.auth import AuthState


class AuthenticationController:
    """Handle login state transitions and notify subscribers."""

    def __init__(
        self,
        initial: Optional[AuthState],
        default_email: Optional[str],
        on_change: Callable[[AuthState], None],
        log: Callable[[str], None],
    ) -> None:
        self.state = initial or AuthState()
        self._default_email = default_email
        self._on_change = on_change
        self._log = log
        self._listeners: List[Callable[[AuthState], None]] = []

    # Subscription ---------------------------------------------------------
    def subscribe(self, callback: Callable[[AuthState], None]) -> None:
        """Register a listener for authentication updates."""

        self._listeners.append(callback)
        callback(self.state)

    # Mutators -------------------------------------------------------------
    def authenticate_with_GroupMint(self, email: str, password: str) -> None:
        """Authenticate using local Group Mint credentials."""

        if "@" not in email or not password or len(password) < 6:
            raise ValueError("Invalid credentials")
        self.state = AuthState(
            is_authenticated=True,
            method="Group Mint",
            email=email,
            token=f"Group Mint-{uuid4().hex[:8]}",
        )
        self._log(f"Signed in as {email} via Group Mint")
        self._notify()

    def logout(self) -> None:
        """Clear the current authentication context."""

        if not self.state.is_authenticated:
            return
        self.state = AuthState()
        self._log("Signed out of the dashboard")
        self._notify()

    def generate_saas_login_url(self) -> str:
        """Return a simulated SaaS login URL."""

        token = f"saas-{uuid4().hex[:8]}"
        self._log("Generated SaaS login link")
        return f"https://saas.example.com/login?token={token}"

    def authenticate_with_token(self, token: str) -> None:
        """Authenticate using a returned SaaS token."""

        if not token:
            raise ValueError("Token required")
        email = self.state.email or self._default_email
        self.state = AuthState(
            is_authenticated=True,
            method="SaaS",
            email=email,
            token=token,
        )
        self._log("SaaS authentication completed")
        self._notify()

    # Internals ------------------------------------------------------------
    def _notify(self) -> None:
        self._on_change(self.state)
        for callback in self._listeners:
            callback(self.state)
