"""Minimal base worker to provide shared utilities for worker classes."""
from __future__ import annotations

from typing import Any, Iterable, List

from app.models import Group


class BaseWorker:
    """Simple base class exposing common attributes for workers."""

    def __init__(self, groupme_client: Any, db_session: Any) -> None:
        self.groupme = groupme_client
        self.db_session = db_session
        self.is_running: bool = False
        self.tenant_id: str | None = getattr(groupme_client, "tenant_id", None)

    async def initialize(self) -> None:  # pragma: no cover - default no-op
        """Hook for worker initialization."""

    async def get_active_groups(self) -> Iterable[Group]:  # pragma: no cover - default no-op
        """Return active groups for the tenant."""
        return []

    async def get_recent_group_activity(self, group_id: str, hours: int = 24) -> List[dict[str, Any]]:  # type: ignore[name-defined]
        """Return mock recent activity for a group."""
        return []
