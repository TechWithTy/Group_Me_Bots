"""Authentication models for the NiceGUI dashboard."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AuthState:
    """Represent the authentication context for the dashboard."""

    is_authenticated: bool = False
    method: str | None = None
    email: str | None = None
    token: str | None = None

    def status_text(self) -> str:
        """Return a human readable summary of the login state."""

        if self.is_authenticated and self.email and self.method:
            return f"Signed in as {self.email} via {self.method}"
        if self.is_authenticated and self.method:
            return f"Signed in via {self.method}"
        return "Not signed in."
