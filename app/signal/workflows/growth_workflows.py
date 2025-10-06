"""Growth and retention workflows for Signal audiences."""
from __future__ import annotations

from typing import Any, Sequence

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = ["SignalInviteAmplificationWorkflow"]


class SignalInviteAmplificationWorkflow(WorkflowDefinition):
    """Amplify growth by sharing invite links and targeted nudges in Signal."""

    name = "signal_invite_amplification"
    title = "Signal Invite Amplification"
    description = (
        "Generates invite links with device-specific deep links and nudges warm "
        "contacts through sealed-sender messages to grow Signal communities."
    )
    goal = "Secure growth by activating qualified contacts with fresh invites."
    kpis = (
        WorkflowKPI("invite_delivery", ">=0.9", "Contacts who receive invites"),
        WorkflowKPI("broadcast_follow_up", "100%", "Groups receiving broadcast update"),
        WorkflowKPI("conversion_floor", ">=5", "Minimum invites issued"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")

        group_id: str = kwargs.get("group_id", "")
        candidate_contacts: Sequence[str] = tuple(kwargs.get("candidate_contacts", ()))
        minimum_invites: int = int(kwargs.get("minimum_invites", 2))
        broadcast_enabled: bool = bool(kwargs.get("broadcast_enabled", True))
        broadcast_message: str = kwargs.get(
            "broadcast_message",
            "🚀 Welcome to the Signal space! New members join via today's invite drop.",
        )

        if not group_id or not candidate_contacts:
            return WorkflowResult(False, {"error": "group_id and candidate_contacts are required"})

        invite_link = await signal_client.create_invite_link(group_id=group_id)

        invites_sent = 0
        for contact in candidate_contacts:
            await signal_client.send_invite(
                group_id=group_id,
                contact=contact,
                invite_link=invite_link,
            )
            invites_sent += 1

        if broadcast_enabled:
            await signal_client.broadcast_update(group_id=group_id, text=broadcast_message)

        achieved = invites_sent >= max(minimum_invites, len(candidate_contacts))

        metrics = {
            "group_id": group_id,
            "invite_link": invite_link,
            "contacts_targeted": len(candidate_contacts),
            "invites_sent": invites_sent,
            "broadcast_enabled": broadcast_enabled,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)
