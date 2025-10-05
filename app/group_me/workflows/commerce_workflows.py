"""Workflow focused on commerce intent detection."""
from __future__ import annotations

from typing import Any, Sequence

from workers.intent_detector import IntentPlan, run_intent_detection_workflow

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult


class CommerceIntentWorkflow(WorkflowDefinition):
    """Detect commerce intents for downstream monetisation workflows."""

    name = "commerce_intent_detection"
    goal = "Maintain commerce intent precision above 0.8 with <50 LLM calls per group."
    kpis = (
        WorkflowKPI("precision", ">=0.8", "Commerce intent precision"),
        WorkflowKPI("llm_call_volume", "<50", "Model invocations per group"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        messages_api = self._require(context, "messages_api")

        messages: Sequence[str] = kwargs.get("messages", [])
        precision_target: float = kwargs.get("precision_target", 0.8)
        minimum_commerce: int = kwargs.get("minimum_commerce", 1)
        group_id: str | None = kwargs.get("group_id")
        fetch_limit: int = kwargs.get("limit", 20)

        fetched_messages = []
        if group_id:
            response = await messages_api.list_for_group(group_id, limit=fetch_limit)
            fetched_messages = [message.text or "" for message in response.messages]
            if not messages:
                messages = fetched_messages
            else:
                messages = list(messages) + fetched_messages

        intents = []
        for message in messages:
            report = await run_intent_detection_workflow(IntentPlan(message_text=message))
            intents.append(report)

        commerce_intents = sum(1 for report in intents if report.intent == "commerce")
        precision = commerce_intents / len(messages) if messages else 0.0

        metrics = {
            "total_messages": len(messages),
            "commerce_intents": commerce_intents,
            "precision": precision,
            "group_id": group_id,
            "messages_sourced": len(fetched_messages),
        }
        achieved = precision >= precision_target and commerce_intents >= minimum_commerce
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


__all__ = ["CommerceIntentWorkflow"]
