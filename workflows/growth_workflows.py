"""Workflows that emphasise group growth and share link distribution."""
from __future__ import annotations

from typing import Any, Iterable, List, Optional

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult


class GhostInvitationWorkflow(WorkflowDefinition):
    """Generate dynamic share links for stealth invitations."""

    name = "ghost_invitation_share_links"
    goal = "Produce at least 3 valid share links for invite campaigns."
    kpis = (
        WorkflowKPI("valid_share_links", ">=3", "Active share URLs harvested"),
        WorkflowKPI("invitation_conversion", ">=20%", "Ghost invite acceptance"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        groups_api = self._require(context, "groups_api")

        target_groups: Optional[Iterable[str]] = kwargs.get("target_groups")
        minimum_links: int = kwargs.get("minimum_links", 3)

        groups = await groups_api.list()
        links: List[str] = []

        for group in groups:
            if target_groups and group.id not in set(target_groups):
                continue
            if group.share_url:
                links.append(group.share_url)

        metrics = {
            "generated_links": links,
            "minimum_links": minimum_links,
        }
        achieved = len(links) >= minimum_links
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


__all__ = ["GhostInvitationWorkflow"]
