"""Commerce-focused workflow implementations for Discord."""
from __future__ import annotations

from typing import Any, Sequence, List
import discord
from discord.ext import commands

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = [
    "CommerceIntentWorkflow",
]


class CommerceIntentWorkflow(WorkflowDefinition):
    """Detect commerce intents for downstream monetization workflows in Discord."""

    name = "discord_commerce_intent_detection"
    goal = "Maintain commerce intent precision above 0.8 with efficient processing."
    kpis = (
        WorkflowKPI("precision", ">=0.8", "Commerce intent precision"),
        WorkflowKPI("processing_efficiency", "<50", "Messages processed per detection cycle"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        discord_client = self._require(context, "discord_client")

        channel_id: int = kwargs.get("channel_id")
        messages: Sequence[str] = kwargs.get("messages", [])
        precision_target: float = kwargs.get("precision_target", 0.8)
        fetch_limit: int = kwargs.get("limit", 20)

        if not channel_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No channel_id provided"})

        try:
            channel = discord_client.get_channel(channel_id)
            if not channel:
                return WorkflowResult(achieved_goal=False, metrics={"error": "Channel not found"})

            # Fetch messages if not provided
            if not messages:
                fetched_messages = []
                async for message in channel.history(limit=fetch_limit):
                    if message.content and message.author != discord_client.user:
                        fetched_messages.append(message.content)
                messages = fetched_messages

            # Analyze messages for commerce intent
            commerce_intents = 0
            for message_content in messages:
                if self._detect_commerce_intent(message_content):
                    commerce_intents += 1

            precision = commerce_intents / len(messages) if messages else 0.0

            metrics = {
                "total_messages": len(messages),
                "commerce_intents": commerce_intents,
                "precision": precision,
                "precision_target": precision_target,
            }

            achieved = precision >= precision_target
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})

    def _detect_commerce_intent(self, message_content: str) -> bool:
        """Simple commerce intent detection based on keywords."""
        commerce_keywords = [
            "buy", "sell", "purchase", "price", "cost", "payment", "money",
            "shop", "store", "product", "sale", "discount", "offer",
            "bitcoin", "crypto", "trading", "investment", "market"
        ]

        message_lower = message_content.lower()
        return any(keyword in message_lower for keyword in commerce_keywords)


__all__ = [
    "CommerceIntentWorkflow",
]
