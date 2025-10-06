"""
Message Stitching Workflow for Discord Bot.

This workflow stitches multiple messages together based on context,
similar to GroupMe and Telegram implementations but adapted for Discord.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from collections import defaultdict
import discord
from discord.ext import commands

from .base import WorkflowDefinition, WorkflowContext, WorkflowKPI, WorkflowResult


class MessageStitchingWorkflow(WorkflowDefinition):
    """Workflow for stitching messages together based on patterns."""

    name = "discord_message_stitching"
    goal = "Stitch related messages in Discord channels to improve conversation flow."
    kpis = (
        WorkflowKPI("stitched_messages", ">=5", "Messages successfully stitched"),
        WorkflowKPI("stitch_success_rate", ">=0.8", "Success rate of message stitching"),
    )

    def __init__(self, bot: commands.Bot, stitch_timeout: int = 300, max_stitch_length: int = 5):
        self.bot = bot
        self.stitch_timeout = stitch_timeout  # Seconds to wait before stitching
        self.max_stitch_length = max_stitch_length  # Max messages to stitch
        self.pending_messages = defaultdict(list)  # Channel ID -> list of messages
        self.stitch_timers = {}  # Channel ID -> timer

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        """Execute the message stitching workflow."""
        discord_client = self._require(context, "discord_client")

        # Get parameters from kwargs or use defaults
        channel_id = kwargs.get("channel_id")
        if not channel_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No channel_id provided"})

        # Process recent messages in the channel
        try:
            channel = discord_client.get_channel(channel_id)
            if not channel:
                return WorkflowResult(achieved_goal=False, metrics={"error": "Channel not found"})

            # Fetch recent messages
            messages = []
            async for message in channel.history(limit=50):
                if message.author != discord_client.user:  # Don't process our own messages
                    messages.append(message)

            # Process messages for stitching
            stitched_count = 0
            for message in messages:
                self.add_message_to_stitch(message)
                stitched_count += 1

            metrics = {
                "processed_messages": len(messages),
                "stitched_messages": stitched_count,
                "pending_channels": len(self.pending_messages),
            }

            achieved = stitched_count > 0
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})

    def add_message_to_stitch(self, message: discord.Message) -> None:
        """Add a message to the stitching queue."""
        channel_id = message.channel.id
        self.pending_messages[channel_id].append(message)

        # Check if we should stitch now
        if len(self.pending_messages[channel_id]) >= self.max_stitch_length:
            asyncio.create_task(self.stitch_messages(channel_id))
        else:
            # Set or reset timer
            if channel_id in self.stitch_timers:
                self.stitch_timers[channel_id].cancel()

            loop = asyncio.get_event_loop()
            self.stitch_timers[channel_id] = loop.call_later(
                self.stitch_timeout, lambda: asyncio.create_task(self.stitch_messages(channel_id))
            )

    async def stitch_messages(self, channel_id: int) -> None:
        """Stitch messages for a channel and send as one."""
        if channel_id not in self.pending_messages or not self.pending_messages[channel_id]:
            return

        messages = self.pending_messages[channel_id]
        if len(messages) > 1:
            stitched_text = self.create_stitched_text(messages)
            try:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(stitched_text)
            except Exception as e:
                print(f"Failed to send stitched message: {e}")

        # Clear pending messages and timer
        self.pending_messages[channel_id] = []
        if channel_id in self.stitch_timers:
            self.stitch_timers[channel_id].cancel()
            del self.stitch_timers[channel_id]

    def create_stitched_text(self, messages: List[discord.Message]) -> str:
        """Create stitched text from messages."""
        texts = [msg.content for msg in messages if msg.content]
        if len(texts) == 1:
            return texts[0]
        elif len(texts) == 2:
            return f"{texts[0]} ... and {texts[1]}"
        else:
            return texts[0] + " ... " + " ... ".join(texts[1:-1]) + f" ... and {texts[-1]}"

    def check_for_continuation_keywords(self, message: discord.Message) -> bool:
        """Check if message has continuation keywords."""
        continuation_words = ['also', 'and', 'plus', 'furthermore', 'moreover']
        content = message.content.lower() if message.content else ''
        return any(word in content for word in continuation_words)

    async def force_stitch_for_channel(self, channel_id: int) -> None:
        """Force stitch messages for a channel."""
        await self.stitch_messages(channel_id)

    def get_stitch_stats(self) -> Dict[str, Any]:
        """Get stitching statistics."""
        return {
            'pending_channels': len(self.pending_messages),
            'total_pending_messages': sum(len(msgs) for msgs in self.pending_messages.values()),
            'stitch_timeout': self.stitch_timeout,
            'max_stitch_length': self.max_stitch_length
        }


__all__ = ["MessageStitchingWorkflow"]
