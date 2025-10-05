"""Workflows focused on message distribution and reactions."""
from __future__ import annotations

from typing import Any, Sequence
from uuid import uuid4

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult


class MessageStitchingWorkflow(WorkflowDefinition):
    """Stitch and echo high-engagement content across groups."""

    name = "message_stitching_content_echo"
    goal = "Amplify cross-group engagement by echoing at least 5 high-signal messages per run."
    kpis = (
        WorkflowKPI("qualified_messages", ">=5", "Messages stitched across communities"),
        WorkflowKPI("echo_success_rate", ">=0.8", "Share of qualifying messages echoed"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        messages_api = self._require(context, "messages_api")
        content_worker = self._require(context, "content_echo_worker")

        group_id: str = kwargs["group_id"]
        limit: int = kwargs.get("limit", 50)
        target_echoes: int = kwargs.get("target_echoes", 5)

        response = await messages_api.list_for_group(group_id, limit=limit)
        baseline = len(getattr(content_worker, "echo_history", []))

        for message in response.messages:
            payload = {
                "id": message.id,
                "group_id": message.group_id or group_id,
                "user_id": message.user_id,
                "text": message.text or "",
                "name": message.name or "Community Member",
            }
            await content_worker.process_message_for_echo(payload)

        updated = len(getattr(content_worker, "echo_history", []))
        echoed_messages = max(0, updated - baseline)

        metrics = {
            "processed_messages": response.count,
            "echoed_messages": echoed_messages,
            "target_echoes": target_echoes,
        }
        achieved = echoed_messages >= target_echoes
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class AutoLikeFeedbackWorkflow(WorkflowDefinition):
    """Close the feedback loop by reacting to high-value messages."""

    name = "auto_like_feedback_loop"
    goal = "Acknowledge 100% of priority messages with bot reactions."
    kpis = (
        WorkflowKPI("reaction_coverage", "100%", "Messages receiving auto-like"),
        WorkflowKPI("feedback_latency", "<30s", "Time to react after detection"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        messages_api = self._require(context, "messages_api")

        group_id: str = kwargs["group_id"]
        message_ids: Sequence[str] = kwargs.get("message_ids", [])
        reaction_text: str = kwargs.get("reaction_text", "👍")
        feedback_suffix: str = kwargs.get("feedback_suffix", "#CommunityBoost")

        for message_id in message_ids:
            await messages_api.post_to_group(
                group_id=group_id,
                source_guid=str(uuid4()),
                text=f"{reaction_text} {feedback_suffix}",
            )

        metrics = {
            "processed_messages": len(message_ids),
            "reaction_text": reaction_text,
        }
        achieved = len(message_ids) > 0
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


__all__ = [
    "MessageStitchingWorkflow",
    "AutoLikeFeedbackWorkflow",
]
