"""Tracking and analytics workflows for Signal bots."""
from __future__ import annotations

from typing import Any

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = ["SignalRealTimeInsightsWorkflow"]


class SignalRealTimeInsightsWorkflow(WorkflowDefinition):
    """Collect real-time metrics from Signal chats for observability dashboards."""

    name = "signal_realtime_insights"
    title = "Signal Real-Time Insights"
    description = (
        "Pulls live membership, delivery, and quality metrics from Signal groups "
        "to feed central observability pipelines and anomaly detectors."
    )
    goal = "Surface actionable insights with low delivery latency."
    kpis = (
        WorkflowKPI("active_member_floor", ">=20", "Active members in time window"),
        WorkflowKPI("latency_budget", "<2m", "Delivery latency for metrics"),
        WorkflowKPI("metric_freshness", "100%", "Runs with updated metrics"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        tracking_worker = self._require(context, "tracking_worker")

        group_id: str = kwargs.get("group_id", "")
        timeframe_hours: int = int(kwargs.get("timeframe_hours", 24))
        target_active_members: int = int(kwargs.get("target_active_members", 20))
        max_delivery_latency: float = float(kwargs.get("max_delivery_latency", 2.0))

        if not group_id:
            return WorkflowResult(False, {"error": "group_id is required"})

        metrics = await tracking_worker.collect_signal_metrics(group_id, timeframe_hours)
        active_members = int(metrics.get("active_members", 0))
        delivery_latency = float(metrics.get("delivery_latency", max_delivery_latency))

        achieved = active_members >= target_active_members and delivery_latency <= max_delivery_latency

        metrics.update(
            {
                "group_id": group_id,
                "timeframe_hours": timeframe_hours,
                "target_active_members": target_active_members,
                "max_delivery_latency": max_delivery_latency,
            }
        )

        return WorkflowResult(achieved_goal=achieved, metrics=metrics)
