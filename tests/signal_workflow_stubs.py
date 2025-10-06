"""Shared stubs for Signal workflow tests."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List


class StubSignalClient:
    """Async stub mimicking essential Signal client capabilities."""

    def __init__(self, messages: Iterable[Dict[str, Any]]) -> None:
        self._messages: List[Dict[str, Any]] = list(messages)
        self.actions: List[tuple[str, Dict[str, Any]]] = []

    async def fetch_group_messages(self, group_id: str, limit: int) -> List[Dict[str, Any]]:
        return [
            message
            for message in self._messages
            if message.get("group_id") == group_id
        ][:limit]

    async def send_reaction(self, **payload: Any) -> None:
        self.actions.append(("reaction", payload))

    async def send_read_receipt(self, **payload: Any) -> None:
        self.actions.append(("receipt", payload))

    async def send_group_message(self, **payload: Any) -> None:
        self.actions.append(("group_message", payload))

    async def pin_message(self, **payload: Any) -> None:
        self.actions.append(("pin", payload))

    async def forward_to_contact(self, **payload: Any) -> None:
        self.actions.append(("forward", payload))

    async def report_message(self, **payload: Any) -> None:
        self.actions.append(("report", payload))

    async def post_story(self, **payload: Any) -> None:
        self.actions.append(("story", payload))

    async def create_invite_link(self, **payload: Any) -> str:
        link = f"signal://invite/{payload.get('group_id', 'unknown')}"
        self.actions.append(("invite_link", {**payload, "link": link}))
        return link

    async def send_invite(self, **payload: Any) -> None:
        self.actions.append(("invite", payload))

    async def broadcast_update(self, **payload: Any) -> None:
        self.actions.append(("broadcast", payload))


class StubStorageClient:
    """Stub storage backend to capture backup payloads."""

    def __init__(self) -> None:
        self.backups: List[Dict[str, Any]] = []

    async def store_backup(self, **payload: Any) -> None:
        self.backups.append(payload)


class StubIntegrationsClient:
    """Stub integration bridge for cross-network relays."""

    def __init__(self) -> None:
        self.relayed: List[Dict[str, Any]] = []

    async def relay_message(self, **payload: Any) -> None:
        self.relayed.append(payload)


class StubPaymentsClient:
    """Stub payments provider capturing escrow operations."""

    def __init__(self) -> None:
        self.invoices: List[Dict[str, Any]] = []
        self.escrow_releases: List[Dict[str, Any]] = []

    async def create_invoice(self, **payload: Any) -> Dict[str, Any]:
        invoice = {"invoice_id": f"inv-{len(self.invoices)+1}", **payload}
        self.invoices.append(invoice)
        return invoice

    async def release_escrow(self, **payload: Any) -> None:
        self.escrow_releases.append(payload)


class StubTrackingWorker:
    """Stub analytics worker returning deterministic metrics."""

    def __init__(self) -> None:
        self.collected: List[Dict[str, Any]] = []

    async def collect_signal_metrics(self, group_id: str, timeframe_hours: int) -> Dict[str, Any]:
        metrics = {
            "group_id": group_id,
            "timeframe_hours": timeframe_hours,
            "active_members": 42,
            "delivery_latency": 1.2,
        }
        self.collected.append(metrics)
        return metrics


__all__ = [
    "StubIntegrationsClient",
    "StubPaymentsClient",
    "StubSignalClient",
    "StubStorageClient",
    "StubTrackingWorker",
]
