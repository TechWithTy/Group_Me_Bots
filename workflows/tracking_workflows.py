"""Workflows leveraging tracking analytics and browser instrumentation."""
from __future__ import annotations
import importlib.util
from enum import Enum
from typing import Any

_pydantic_spec = importlib.util.find_spec("pydantic")
_tracking_spec = importlib.util.find_spec("_schema.tracking")
if _tracking_spec is not None and _pydantic_spec is not None:
    from _schema.tracking import BrowserAction
else:
    class BrowserAction(str, Enum):  # type: ignore[too-many-ancestors]
        """Fallback browser actions when tracking schema is unavailable."""

        NAVIGATE = "navigate"
        CLICK = "click"
        TYPE = "type"
        SCROLL = "scroll"
        WAIT = "wait"
        SCREENSHOT = "screenshot"
        EXTRACT = "extract"

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult


class RealTimeSubscriptionWorkflow(WorkflowDefinition):
    """Capture near real-time engagement events via long polling."""

    name = "real_time_event_capture"
    goal = "Capture 95% of high-signal events within the last polling window."
    kpis = (
        WorkflowKPI("event_capture_rate", ">=0.95", "Share of events logged"),
        WorkflowKPI("mean_latency", "<2s", "Average delay from detection to log"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        messages_api = self._require(context, "messages_api")
        tracking_worker = self._require(context, "tracking_worker")

        group_id: str = kwargs["group_id"]
        limit: int = kwargs.get("limit", 20)
        minimum_events: int = kwargs.get("minimum_events", 1)

        response = await messages_api.list_for_group(group_id, limit=limit)
        captured = 0

        for message in response.messages:
            await tracking_worker.track_browser_interaction(
                url=f"groupme://groups/{group_id}/messages/{message.id}",
                action=BrowserAction.NAVIGATE,
                parameters={
                    "group_id": group_id,
                    "message_id": message.id,
                    "user_id": message.user_id,
                },
                result={"text": message.text or ""},
            )
            captured += 1

        metrics = {
            "captured_events": captured,
            "minimum_events": minimum_events,
        }
        achieved = captured >= minimum_events
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class ContentMiningWorkflow(WorkflowDefinition):
    """Blend content mining insights with tracking analytics."""

    name = "content_mining_micro_targeting"
    goal = "Surface at least two trending topics for micro-targeting daily."
    kpis = (
        WorkflowKPI("trending_topics", ">=2", "Trending topics identified"),
        WorkflowKPI("insight_latency", "<1h", "Time to refresh mining output"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        content_worker = self._require(context, "content_echo_worker")
        tracking_worker = self._require(context, "tracking_worker")

        mining_snapshot = await content_worker.run_content_mining()
        analytics_snapshot = await tracking_worker.get_comprehensive_analytics()

        topics = mining_snapshot.get("trending_topics", [])
        minimum_topics: int = kwargs.get("minimum_topics", 2)

        metrics = {
            "trending_topics": topics,
            "analytics_snapshot": analytics_snapshot,
            "minimum_topics": minimum_topics,
        }
        achieved = len(topics) >= minimum_topics
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


__all__ = [
    "RealTimeSubscriptionWorkflow",
    "ContentMiningWorkflow",
]
