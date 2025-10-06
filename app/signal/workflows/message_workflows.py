"""Message-centric workflow implementations for Signal."""
from __future__ import annotations

from typing import Any, Sequence, List, Dict
import asyncio

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = [
    "SignalMessageStitchingWorkflow",
    "SignalSecurityModerationWorkflow",
    "SignalContentEchoWorkflow",
]


class SignalMessageStitchingWorkflow(WorkflowDefinition):
    """Stitch and echo high-engagement content across Signal groups."""

    name = "signal_message_stitching_content_echo"
    goal = "Amplify cross-group engagement by echoing at least 5 high-signal messages per run."
    kpis = (
        WorkflowKPI("qualified_messages", ">=5", "Messages stitched across groups"),
        WorkflowKPI("echo_success_rate", ">=0.8", "Share of qualifying messages echoed"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")
        groups_api = self._require(context, "groups_api")

        group_id: str = kwargs.get("group_id")
        limit: int = kwargs.get("limit", 50)
        target_echoes: int = kwargs.get("target_echoes", 5)

        if not group_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No group_id provided"})

        try:
            # Get group messages (Signal API would need to be implemented)
            # For now, simulate the process
            messages = await self._get_group_messages(signal_client, group_id, limit)

            # Process messages for stitching
            stitched_messages = []
            for message in messages[:10]:  # Process first 10 for demo
                if self._is_high_engagement_message(message):
                    stitched_messages.append(message)

            # Echo to other groups (simulated)
            echoed_count = min(len(stitched_messages), target_echoes)

            metrics = {
                "processed_messages": len(messages),
                "stitched_messages": len(stitched_messages),
                "echoed_messages": echoed_count,
                "target_echoes": target_echoes,
            }

            achieved = echoed_count >= target_echoes
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})

    async def _get_group_messages(self, signal_client, group_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get messages from Signal group (would use Signal API)."""
        # Simulate API call
        await asyncio.sleep(0.1)
        return [
            {"id": f"msg_{i}", "content": f"Message {i}", "author": f"user_{i % 3}"}
            for i in range(min(limit, 20))
        ]

    def _is_high_engagement_message(self, message: Dict[str, Any]) -> bool:
        """Check if message has high engagement potential."""
        content = message.get("content", "").lower()
        # Simple heuristic - messages with questions or positive keywords
        return "?" in content or any(word in content for word in ["great", "awesome", "thanks"])


class SignalSecurityModerationWorkflow(WorkflowDefinition):
    """Monitors for spam, inappropriate content, or policy violations in Signal groups."""

    name = "signal_security_moderation_monitoring"
    goal = "Detect and flag 95% of inappropriate content within 5 minutes."
    kpis = (
        WorkflowKPI("detection_rate", ">=0.95", "Inappropriate content detection rate"),
        WorkflowKPI("response_time", "<300s", "Time to respond to violations"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")
        groups_api = self._require(context, "groups_api")

        group_id: str = kwargs.get("group_id")
        moderation_keywords: list = kwargs.get("moderation_keywords",
            ["spam", "inappropriate", "offensive", "violation"])

        if not group_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No group_id provided"})

        try:
            # Get recent messages
            messages = await self._get_group_messages(signal_client, group_id, 100)

            violations = []
            for message in messages:
                content = message.get("content", "").lower()
                if any(keyword in content for keyword in moderation_keywords):
                    violations.append(message)

            # Flag violations
            flagged_count = len(violations)

            metrics = {
                "processed_messages": len(messages),
                "violations_detected": flagged_count,
                "moderation_keywords": moderation_keywords,
            }

            achieved = flagged_count / len(messages) < 0.05 if messages else True
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


class SignalContentEchoWorkflow(WorkflowDefinition):
    """Echo and share engaging content across Signal groups."""

    name = "signal_content_echo"
    goal = "Share high-engagement content across groups to boost overall activity."
    kpis = (
        WorkflowKPI("echo_engagement_rate", ">=0.7", "Engagement rate of echoed content"),
        WorkflowKPI("cross_group_reach", ">=5", "Groups reached per echo cycle"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")
        groups_api = self._require(context, "groups_api")

        source_group_id: str = kwargs.get("source_group_id")
        target_group_ids: Sequence[str] = kwargs.get("target_group_ids", [])

        if not source_group_id or not target_group_ids:
            return WorkflowResult(achieved_goal=False, metrics={"error": "Missing source or target groups"})

        try:
            # Get recent messages from source group
            messages = await self._get_group_messages(signal_client, source_group_id, 20)

            echoed_count = 0
            for message in messages[:5]:  # Echo top 5 messages
                echo_text = f"💬 From group: {message.get('content', '')}"

                # Send to target groups
                for target_group_id in target_group_ids:
                    try:
                        # In real implementation, use Signal API to send message
                        await self._send_to_group(signal_client, target_group_id, echo_text)
                        echoed_count += 1
                    except Exception as e:
                        print(f"Failed to echo to group {target_group_id}: {e}")

            metrics = {
                "source_messages": len(messages),
                "echoed_messages": echoed_count,
                "target_groups": len(target_group_ids),
            }

            achieved = echoed_count >= len(target_group_ids) * 2
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
        await asyncio.sleep(0.05)  # Simulate API call


__all__ = [
    "SignalMessageStitchingWorkflow",
    "SignalSecurityModerationWorkflow",
    "SignalContentEchoWorkflow",
]
