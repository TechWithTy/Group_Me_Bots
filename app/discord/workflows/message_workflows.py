"""Message-centric workflow implementations for Discord."""
from __future__ import annotations

from typing import Any, Sequence
import discord
from discord.ext import commands

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = [
    "MessageStitchingWorkflow",
    "SecurityModerationWorkflow",
    "ContentEchoWorkflow",
]


class MessageStitchingWorkflow(WorkflowDefinition):
    """Stitch and echo high-engagement content across Discord channels."""

    title = "Discord Message Stitching"
    description = "Stitch related Discord messages and rebroadcast highlights across communities."
    name = "discord_message_stitching_content_echo"
    goal = "Amplify cross-channel engagement by echoing at least 5 high-signal messages per run."
    kpis = (
        WorkflowKPI("qualified_messages", ">=5", "Messages stitched across channels"),
        WorkflowKPI("echo_success_rate", ">=0.8", "Share of qualifying messages echoed"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        discord_client = self._require(context, "discord_client")
        content_worker = self._require(context, "content_echo_worker")

        channel_id: int = kwargs.get("channel_id")
        limit: int = kwargs.get("limit", 50)
        target_echoes: int = kwargs.get("target_echoes", 5)

        if not channel_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No channel_id provided"})

        try:
            channel = discord_client.get_channel(channel_id)
            if not channel:
                return WorkflowResult(achieved_goal=False, metrics={"error": "Channel not found"})

            response = []
            async for message in channel.history(limit=limit):
                if message.author != discord_client.user:
                    response.append(message)

            baseline = len(getattr(content_worker, "echo_history", []))

            for message in response:
                payload = {
                    "id": str(message.id),
                    "channel_id": str(message.channel.id),
                    "user_id": str(message.author.id),
                    "text": message.content or "",
                    "author_name": message.author.name or "Community Member",
                }
                await content_worker.process_message_for_echo(payload)

            updated = len(getattr(content_worker, "echo_history", []))
            echoed_messages = max(0, updated - baseline)

            metrics = {
                "processed_messages": len(response),
                "echoed_messages": echoed_messages,
                "target_echoes": target_echoes,
            }
            achieved = echoed_messages >= target_echoes
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})


class SecurityModerationWorkflow(WorkflowDefinition):
    """Monitors for spam, inappropriate content, or policy violations in Discord channels."""

    title = "Discord Security Moderation"
    description = "Detect and escalate potential policy violations within Discord channels."
    name = "discord_security_moderation_monitoring"
    goal = "Detect and flag 95% of inappropriate content within 5 minutes."
    kpis = (
        WorkflowKPI("detection_rate", ">=0.95", "Inappropriate content detection rate"),
        WorkflowKPI("response_time", "<300s", "Time to respond to violations"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        discord_client = self._require(context, "discord_client")

        channel_id: int = kwargs.get("channel_id")
        moderation_keywords: list = kwargs.get("moderation_keywords",
            ["spam", "inappropriate", "offensive", "violation"])

        if not channel_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No channel_id provided"})

        try:
            channel = discord_client.get_channel(channel_id)
            if not channel:
                return WorkflowResult(achieved_goal=False, metrics={"error": "Channel not found"})

            messages = []
            async for message in channel.history(limit=100):
                if message.author != discord_client.user:
                    messages.append(message)

            violations = []
            for message in messages:
                content = message.content.lower() if message.content else ""
                if any(keyword in content for keyword in moderation_keywords):
                    violations.append(message)

            # Flag violations (in a real implementation, you'd log or take action)
            flagged_count = len(violations)

            metrics = {
                "processed_messages": len(messages),
                "violations_detected": flagged_count,
            }
            achieved = flagged_count / len(messages) < 0.05 if messages else True  # Less than 5% violations
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})


class ContentEchoWorkflow(WorkflowDefinition):
    """Echo and share engaging content across Discord channels."""

    title = "Discord Content Echo"
    description = "Amplify standout Discord conversations by echoing them to target communities."
    name = "discord_content_echo"
    goal = "Share high-engagement content across channels to boost overall activity."
    kpis = (
        WorkflowKPI("echo_engagement_rate", ">=0.7", "Engagement rate of echoed content"),
        WorkflowKPI("cross_channel_reach", ">=10", "Channels reached per echo cycle"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        discord_client = self._require(context, "discord_client")
        content_worker = self._require(context, "content_echo_worker")

        source_channel_id: int = kwargs.get("source_channel_id")
        target_channel_ids: Sequence[int] = kwargs.get("target_channel_ids", [])

        if not source_channel_id or not target_channel_ids:
            return WorkflowResult(achieved_goal=False, metrics={"error": "Missing source or target channels"})

        try:
            source_channel = discord_client.get_channel(source_channel_id)
            if not source_channel:
                return WorkflowResult(achieved_goal=False, metrics={"error": "Source channel not found"})

            # Get recent messages from source channel
            messages = []
            async for message in source_channel.history(limit=20):
                if message.author != discord_client.user and message.content:
                    messages.append(message)

            echoed_count = 0
            for message in messages[:5]:  # Echo top 5 messages
                payload = {
                    "id": str(message.id),
                    "channel_id": str(message.channel.id),
                    "user_id": str(message.author.id),
                    "text": message.content,
                    "author_name": message.author.name,
                }

                # Process for echoing to target channels
                for target_channel_id in target_channel_ids:
                    target_channel = discord_client.get_channel(target_channel_id)
                    if target_channel:
                        try:
                            echo_text = f"💬 From {message.author.name}: {message.content}"
                            await target_channel.send(echo_text)
                            echoed_count += 1
                        except Exception as e:
                            print(f"Failed to echo to channel {target_channel_id}: {e}")

            metrics = {
                "source_messages": len(messages),
                "echoed_messages": echoed_count,
                "target_channels": len(target_channel_ids),
            }
            achieved = echoed_count >= len(target_channel_ids) * 2  # At least 2 echoes per channel
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})


__all__ = [
    "MessageStitchingWorkflow",
    "SecurityModerationWorkflow",
    "ContentEchoWorkflow",
]
