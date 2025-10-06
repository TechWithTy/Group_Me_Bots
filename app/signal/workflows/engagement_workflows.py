"""Engagement-focused workflow implementations for Signal."""
from __future__ import annotations

from typing import Any, Sequence, List, Dict
import asyncio

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = [
    "SignalAutoLikeFeedbackWorkflow",
    "SignalContentQualityWorkflow",
    "SignalEmergencyResponseWorkflow",
]


class SignalAutoLikeFeedbackWorkflow(WorkflowDefinition):
    """Close the feedback loop by reacting to high-value messages in Signal."""

    name = "signal_auto_like_feedback"
    goal = "Acknowledge high-value messages with reactions to boost engagement."
    kpis = (
        WorkflowKPI("reaction_coverage", ">=0.8", "Messages receiving reactions"),
        WorkflowKPI("feedback_engagement", ">=0.7", "User engagement after reactions"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")
        groups_api = self._require(context, "groups_api")

        group_id: str = kwargs.get("group_id")
        message_ids: Sequence[str] = kwargs.get("message_ids", [])
        reaction_emoji: str = kwargs.get("reaction_emoji", "👍")

        if not group_id or not message_ids:
            return WorkflowResult(achieved_goal=False, metrics={"error": "Missing group_id or message_ids"})

        try:
            reacted_count = 0
            for message_id in message_ids[:10]:  # Process first 10 for demo
                try:
                    # In real Signal implementation, send reaction
                    await self._send_reaction(signal_client, group_id, message_id, reaction_emoji)
                    reacted_count += 1
                except Exception as e:
                    print(f"Failed to react to message {message_id}: {e}")

            metrics = {
                "processed_messages": len(message_ids),
                "reacted_messages": reacted_count,
                "reaction_emoji": reaction_emoji,
            }

            achieved = reacted_count / len(message_ids) >= 0.8 if message_ids else False
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})

    async def _send_reaction(self, signal_client, group_id: str, message_id: str, emoji: str):
        """Send reaction to Signal message."""
        await asyncio.sleep(0.05)  # Simulate API call


class SignalContentQualityWorkflow(WorkflowDefinition):
    """Assess and promote high-quality, relevant content in Signal groups."""

    name = "signal_content_quality_relevance"
    goal = "Identify and highlight 90% of high-quality messages for better group experience."
    kpis = (
        WorkflowKPI("quality_detection_rate", ">=0.9", "High-quality messages correctly identified"),
        WorkflowKPI("promotion_effectiveness", ">=0.8", "Success rate of content promotion"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")
        groups_api = self._require(context, "groups_api")

        group_id: str = kwargs.get("group_id")
        message_limit: int = kwargs.get("message_limit", 50)

        if not group_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No group_id provided"})

        try:
            messages = await self._get_group_messages(signal_client, group_id, message_limit)

            quality_messages = []
            for message in messages:
                quality_score = self._assess_message_quality(message)
                if quality_score >= 0.7:
                    quality_messages.append(message)

            # Promote quality messages (simulate pinning or highlighting)
            promoted_count = 0
            for message in quality_messages[:5]:  # Promote top 5
                # In real implementation, might pin message or send highlight
                promoted_count += 1

            metrics = {
                "processed_messages": len(messages),
                "quality_messages": len(quality_messages),
                "promoted_messages": promoted_count,
            }

            achieved = len(quality_messages) / len(messages) >= 0.5 if messages else False
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})

    async def _get_group_messages(self, signal_client, group_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get messages from Signal group."""
        await asyncio.sleep(0.1)
        return [
            {"id": f"msg_{i}", "content": f"Message {i}", "author": f"user_{i % 3}"}
            for i in range(min(limit, 20))
        ]

    def _assess_message_quality(self, message: Dict[str, Any]) -> float:
        """Assess the quality of a message based on various factors."""
        content = message.get("content", "").lower()

        # Length factor
        length_score = min(1.0, len(content) / 100) if len(content) > 10 else 0.3

        # Keyword factor
        positive_keywords = ['great', 'excellent', 'awesome', 'helpful', 'thanks', 'good']
        keyword_score = sum(1 for keyword in positive_keywords if keyword in content) / len(positive_keywords)

        return (length_score * 0.5 + keyword_score * 0.5)


class SignalEmergencyResponseWorkflow(WorkflowDefinition):
    """Handle emergency situations and critical alerts in Signal groups."""

    name = "signal_emergency_response"
    goal = "Respond to 100% of emergency situations within 2 minutes."
    kpis = (
        WorkflowKPI("emergency_detection_rate", "100%", "Emergency situations correctly identified"),
        WorkflowKPI("response_time", "<120s", "Time to respond to emergencies"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")
        groups_api = self._require(context, "groups_api")

        group_id: str = kwargs.get("group_id")
        emergency_keywords: list = kwargs.get("emergency_keywords",
            ["emergency", "urgent", "critical", "help", "911"])

        if not group_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No group_id provided"})

        try:
            messages = await self._get_group_messages(signal_client, group_id, 20)

            emergencies = []
            for message in messages:
                content = message.get("content", "").lower()
                if any(keyword in content for keyword in emergency_keywords):
                    emergencies.append(message)

            # Respond to emergencies
            responded_count = 0
            for message in emergencies:
                # Send emergency response
                response = "🚨 **EMERGENCY DETECTED** 🚨\nPlease stay calm. Help is on the way!"
                await self._send_to_group(signal_client, group_id, response)
                responded_count += 1

            metrics = {
                "processed_messages": len(messages),
                "emergencies_detected": len(emergencies),
                "emergency_responses": responded_count,
            }

            achieved = responded_count == len(emergencies)
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})

    async def _get_group_messages(self, signal_client, group_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get messages from Signal group."""
        await asyncio.sleep(0.1)
        return [
            {"id": f"msg_{i}", "content": f"Message {i}", "author": f"user_{i % 3}"}
            for i in range(min(limit, 10))
        ]

    async def _send_to_group(self, signal_client, group_id: str, message: str):
        """Send message to Signal group."""
        await asyncio.sleep(0.05)


__all__ = [
    "SignalAutoLikeFeedbackWorkflow",
    "SignalContentQualityWorkflow",
    "SignalEmergencyResponseWorkflow",
]
