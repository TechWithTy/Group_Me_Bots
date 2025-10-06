"""Engagement-focused workflow implementations for Signal."""
from __future__ import annotations

from typing import Any, List, Sequence

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = [
    "SignalAutoLikeFeedbackWorkflow",
    "SignalContentQualityWorkflow",
    "SignalEmergencyResponseWorkflow",
]


class SignalAutoLikeFeedbackWorkflow(WorkflowDefinition):
    """Send reactions, read receipts, and acknowledgements in bulk."""

    name = "signal_auto_like_feedback"
    title = "Signal Auto Reaction Feedback"
    description = (
        "Automatically react to priority messages, send read receipts, and acknowledge"
        " senders using Signal's advanced messaging APIs."
    )
    goal = "Acknowledge high-value messages and confirm delivery in near real-time."
    kpis = (
        WorkflowKPI("reaction_coverage", ">=0.8", "Share of priority messages reacted to"),
        WorkflowKPI("read_receipts", "100%", "Receipts sent for acknowledged messages"),
        WorkflowKPI("ack_latency", "<30s", "Latency from detection to acknowledgement"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")

        group_id: str = kwargs.get("group_id", "")
        message_ids: Sequence[str] = tuple(kwargs.get("message_ids", ()))
        reaction_emoji: str = kwargs.get("reaction_emoji", "👍")
        send_receipts: bool = kwargs.get("send_receipts", True)
        acknowledge_text: str = kwargs.get(
            "acknowledge_text", "Thanks for the update!"
        )
        minimum_coverage: float = kwargs.get("minimum_coverage", 0.8)

        if not group_id or not message_ids:
            return WorkflowResult(
                achieved_goal=False,
                metrics={"error": "group_id and message_ids are required"},
            )

        reactions_sent = 0
        receipts_sent = 0
        acknowledgements: List[str] = []
        failures: List[str] = []

        for message_id in message_ids:
            try:
                await signal_client.send_reaction(
                    group_id=group_id,
                    message_id=message_id,
                    emoji=reaction_emoji,
                )
                reactions_sent += 1

                if send_receipts:
                    await signal_client.send_read_receipt(
                        group_id=group_id,
                        message_id=message_id,
                    )
                    receipts_sent += 1

                if acknowledge_text:
                    await signal_client.send_group_message(
                        group_id=group_id,
                        text=f"{reaction_emoji} {acknowledge_text}",
                        reply_to=message_id,
                    )
                    acknowledgements.append(message_id)
            except Exception as exc:  # pragma: no cover - defensive logging
                failures.append(f"{message_id}:{exc}")

        total_processed = len(message_ids)
        coverage = reactions_sent / total_processed if total_processed else 0.0
        achieved = coverage >= minimum_coverage and (not send_receipts or receipts_sent == reactions_sent)

        metrics = {
            "group_id": group_id,
            "processed_messages": total_processed,
            "reactions_sent": reactions_sent,
            "read_receipts_sent": receipts_sent,
            "acknowledged_messages": len(acknowledgements),
            "reaction_emoji": reaction_emoji,
            "failures": failures,
            "coverage": coverage,
            "minimum_coverage": minimum_coverage,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class SignalContentQualityWorkflow(WorkflowDefinition):
    """Score content and promote the highest quality posts in a group."""

    name = "signal_content_quality_relevance"
    title = "Signal Content Quality & Highlights"
    description = (
        "Reviews recent Signal messages, scores quality using heuristics, and highlights"
        " the best content via pinned or boosted announcements."
    )
    goal = "Maintain a high quality bar by highlighting the top 20% of messages."
    kpis = (
        WorkflowKPI("quality_detection_rate", ">=0.9", "High-quality messages identified"),
        WorkflowKPI("highlight_coverage", ">=0.2", "Share of messages highlighted"),
        WorkflowKPI("attachment_engagement", ">=0.6", "Engagement on media-rich content"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")

        group_id: str = kwargs.get("group_id", "")
        limit: int = int(kwargs.get("limit", 50))
        highlight_limit: int = int(kwargs.get("highlight_limit", 3))
        attachment_weight: float = float(kwargs.get("attachment_weight", 0.15))

        if not group_id:
            return WorkflowResult(False, {"error": "group_id is required"})

        messages = list(
            await signal_client.fetch_group_messages(
                group_id=group_id,
                limit=limit,
            )
        )

        scored_messages: List[tuple[float, dict[str, Any]]] = []
        for message in messages:
            score = self._score_message(message, attachment_weight)
            scored_messages.append((score, message))

        scored_messages.sort(key=lambda item: item[0], reverse=True)
        highlights = scored_messages[:highlight_limit]

        promoted_ids: List[str] = []
        for score, message in highlights:
            try:
                await signal_client.pin_message(group_id=group_id, message_id=message["id"])
                promoted_ids.append(message["id"])
            except Exception as exc:  # pragma: no cover - defensive logging
                promoted_ids.append(f"failed:{message['id']}:{exc}")

        processed = len(scored_messages)
        quality_messages = len([score for score, _ in scored_messages if score >= 0.7])
        highlight_ratio = (len(promoted_ids) / processed) if processed else 0.0
        achieved = processed > 0 and highlight_ratio >= 0.2

        metrics = {
            "group_id": group_id,
            "processed_messages": processed,
            "quality_messages": quality_messages,
            "highlighted_messages": len(promoted_ids),
            "highlight_ratio": highlight_ratio,
            "attachment_weight": attachment_weight,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)

    @staticmethod
    def _score_message(message: dict[str, Any], attachment_weight: float) -> float:
        content = str(message.get("text") or message.get("content") or "").lower()
        reactions = int(message.get("reactions", 0))
        attachments: Sequence[dict[str, Any]] = tuple(message.get("attachments", ()))

        keyword_bonus = 0.0
        for keyword in ("launch", "update", "thanks", "great", "awesome", "guide"):
            if keyword in content:
                keyword_bonus += 0.1

        attachment_bonus = min(len(attachments) * attachment_weight, 0.3)
        reaction_bonus = min(reactions / 10.0, 0.4)
        base_score = 0.4 if len(content) >= 20 else 0.2

        return min(1.0, base_score + keyword_bonus + attachment_bonus + reaction_bonus)


class SignalEmergencyResponseWorkflow(WorkflowDefinition):
    """Detect urgent signals and broadcast emergency instructions."""

    name = "signal_emergency_response"
    title = "Signal Emergency Response"
    description = (
        "Scans incoming Signal conversations for emergency keywords, escalates to on-call"
        " responders, and posts safety guidance back to the group."
    )
    goal = "Respond to every detected emergency message within the run."
    kpis = (
        WorkflowKPI("emergency_detection_rate", "100%", "Detected emergency keywords"),
        WorkflowKPI("response_broadcasts", ">=1", "Safety broadcasts delivered"),
        WorkflowKPI("escalations", ">=1", "Escalations sent to on-call contacts"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")

        group_id: str = kwargs.get("group_id", "")
        emergency_keywords: Sequence[str] = tuple(
            kw.lower() for kw in kwargs.get(
                "emergency_keywords", ("emergency", "urgent", "help", "accident", "fire")
            )
        )
        escalation_contact: str | None = kwargs.get("escalation_contact")
        guidance_message: str = kwargs.get(
            "guidance_message",
            "🚨 Emergency team has been notified. Follow safety protocols and await instructions.",
        )

        if not group_id:
            return WorkflowResult(False, {"error": "group_id is required"})

        messages = list(
            await signal_client.fetch_group_messages(
                group_id=group_id,
                limit=int(kwargs.get("limit", 30)),
            )
        )

        emergencies: List[dict[str, Any]] = []
        for message in messages:
            text = str(message.get("text") or message.get("content") or "").lower()
            if any(keyword in text for keyword in emergency_keywords):
                emergencies.append(message)

        for emergency in emergencies:
            await signal_client.send_group_message(
                group_id=group_id,
                text=guidance_message,
                reply_to=emergency.get("id"),
            )
            if escalation_contact:
                await signal_client.forward_to_contact(
                    contact=escalation_contact,
                    message=emergency,
                )

        achieved = bool(emergencies)
        metrics = {
            "group_id": group_id,
            "emergencies_detected": len(emergencies),
            "broadcasts_sent": len(emergencies),
            "escalations": len(emergencies) if escalation_contact else 0,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)
