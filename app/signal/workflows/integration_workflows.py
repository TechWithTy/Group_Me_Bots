"""Integration workflows bridging Signal with other collaboration surfaces."""
from __future__ import annotations

from typing import Any

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = ["SignalCrossNetworkRelayWorkflow"]


class SignalCrossNetworkRelayWorkflow(WorkflowDefinition):
    """Relay curated Signal payloads into partner platforms with receipts."""

    name = "signal_cross_network_relay"
    title = "Signal Cross-Network Relay"
    description = (
        "Bridges Signal conversations into Telegram, GroupMe, or custom webhooks "
        "using signed envelopes for downstream attribution and analytics."
    )
    goal = "Deliver Signal payloads to every configured downstream platform."
    kpis = (
        WorkflowKPI("relay_success_rate", ">=0.9", "Relays acknowledged by targets"),
        WorkflowKPI("platform_coverage", "100%", "Platforms receiving payloads"),
        WorkflowKPI("latency_budget", "<5s", "Average relay latency"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        integrations_client = self._require(context, "integrations_client")

        payloads: tuple[dict[str, Any], ...] = tuple(kwargs.get("payloads", ()))
        target_platforms: tuple[str, ...] = tuple(kwargs.get("target_platforms", ()))
        success_threshold: float = float(kwargs.get("success_threshold", 0.9))
        signature_tag: str = kwargs.get("signature_tag", "signal_bridge")

        if not payloads or not target_platforms:
            return WorkflowResult(False, {"error": "payloads and target_platforms are required"})

        relayed = 0
        envelopes = 0

        for payload in payloads:
            for platform in target_platforms:
                await integrations_client.relay_message(
                    platform=platform,
                    payload=payload,
                    signature_tag=signature_tag,
                    metadata={"source": "signal"},
                )
                relayed += 1
            envelopes += 1

        total_expected = len(payloads) * len(target_platforms)
        success_rate = relayed / total_expected if total_expected else 0.0
        achieved = success_rate >= success_threshold and envelopes > 0

        metrics = {
            "payloads_processed": len(payloads),
            "platforms": len(target_platforms),
            "relays_sent": relayed,
            "success_rate": success_rate,
            "signature_tag": signature_tag,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)
