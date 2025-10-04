"""Shared workflow definitions and context helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Sequence


@dataclass(slots=True)
class WorkflowKPI:
    """Represents an individual KPI for a workflow."""

    name: str
    target: str
    description: str


@dataclass(slots=True)
class WorkflowResult:
    """Aggregate result returned by workflow execution."""

    achieved_goal: bool
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowContext:
    """Holds worker and API dependencies shared across workflows."""

    messages_api: Optional["MessagesAPI"] = None
    bots_api: Optional["BotsAPI"] = None
    chats_api: Optional["ChatsAPI"] = None
    groups_api: Optional["GroupsAPI"] = None
    engagement_worker: Optional["EngagementWorker"] = None
    content_echo_worker: Optional["ContentEchoWorker"] = None
    tracking_worker: Optional["TrackingWorker"] = None


class WorkflowDefinition:
    """Base class for all orchestrated workflows."""

    name: str
    goal: str
    kpis: Sequence[WorkflowKPI]

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:  # pragma: no cover - interface
        raise NotImplementedError

    @staticmethod
    def _require(context: WorkflowContext, attribute: str) -> Any:
        value = getattr(context, attribute)
        if value is None:
            raise ValueError(f"Workflow requires '{attribute}' in context")
        return value


__all__ = [
    "WorkflowKPI",
    "WorkflowResult",
    "WorkflowContext",
    "WorkflowDefinition",
]
