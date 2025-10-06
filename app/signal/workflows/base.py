"""Base workflow definitions for Signal bot."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
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

    signal_client: Optional[Any] = None  # Signal client
    messages_api: Optional[Any] = None
    groups_api: Optional[Any] = None
    contacts_api: Optional[Any] = None
    engagement_worker: Optional[Any] = None
    tracking_worker: Optional[Any] = None
    storage_client: Optional[Any] = None
    integrations_client: Optional[Any] = None
    payments_client: Optional[Any] = None


class WorkflowDefinition:
    """Base class for all orchestrated workflows."""

    name: str
    title: str
    description: str
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

    def describe(self) -> Dict[str, Any]:
        """Return a machine-readable description of the workflow."""

        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "goal": self.goal,
            "kpis": [asdict(kpi) for kpi in self.kpis],
        }


__all__ = [
    "WorkflowKPI",
    "WorkflowResult",
    "WorkflowContext",
    "WorkflowDefinition",
]
