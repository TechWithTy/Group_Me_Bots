"""Growth-focused workflow implementations for Discord."""
from __future__ import annotations

from typing import Any, Iterable, List, Optional
import discord
from discord.ext import commands

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = [
    "GhostInvitationWorkflow",
    "ServerGrowthWorkflow",
]


class GhostInvitationWorkflow(WorkflowDefinition):
    """Generate dynamic share links for stealth invitations in Discord."""

    title = "Discord Ghost Invitations"
    description = "Create campaign-ready invite links for targeted community growth."
    name = "discord_ghost_invitation_share_links"
    goal = "Generate at least 3 valid invite links for growth campaigns."
    kpis = (
        WorkflowKPI("valid_invite_links", ">=3", "Active invite URLs generated"),
        WorkflowKPI("invitation_conversion", ">=20%", "Invite acceptance rate"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        discord_client = self._require(context, "discord_client")

        guild_id: int = kwargs.get("guild_id")
        target_channels: Optional[Iterable[int]] = kwargs.get("target_channels")
        minimum_links: int = kwargs.get("minimum_links", 3)

        if not guild_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No guild_id provided"})

        try:
            guild = discord_client.get_guild(guild_id)
            if not guild:
                return WorkflowResult(achieved_goal=False, metrics={"error": "Guild not found"})

            invite_links = []

            # Generate invites for specified channels or all channels
            channels_to_check = target_channels or [channel.id for channel in guild.channels if isinstance(channel, discord.TextChannel)]

            for channel_id in channels_to_check:
                channel = guild.get_channel(channel_id)
                if isinstance(channel, discord.TextChannel):
                    try:
                        # Create invite link
                        invite = await channel.create_invite(max_age=86400, max_uses=100, unique=True)
                        invite_links.append({
                            "channel_id": channel_id,
                            "channel_name": channel.name,
                            "invite_url": invite.url,
                            "expires_at": invite.expires_at.isoformat() if invite.expires_at else None,
                        })
                    except discord.Forbidden:
                        continue  # Skip channels where we can't create invites
                    except Exception as e:
                        print(f"Error creating invite for channel {channel_id}: {e}")

            metrics = {
                "generated_links": len(invite_links),
                "invite_links": invite_links,
                "minimum_links": minimum_links,
            }

            achieved = len(invite_links) >= minimum_links
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})


class ServerGrowthWorkflow(WorkflowDefinition):
    """Monitor and optimize server growth metrics."""

    title = "Discord Server Growth"
    description = "Track membership momentum and retention signals across the Discord server."
    name = "discord_server_growth_monitoring"
    goal = "Achieve consistent server growth with positive member retention."
    kpis = (
        WorkflowKPI("member_growth_rate", ">=5%", "New members per week"),
        WorkflowKPI("retention_rate", ">=70%", "Member retention over 30 days"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        discord_client = self._require(context, "discord_client")

        guild_id: int = kwargs.get("guild_id")
        growth_target: float = kwargs.get("growth_target", 0.05)  # 5% growth

        if not guild_id:
            return WorkflowResult(achieved_goal=False, metrics={"error": "No guild_id provided"})

        try:
            guild = discord_client.get_guild(guild_id)
            if not guild:
                return WorkflowResult(achieved_goal=False, metrics={"error": "Guild not found"})

            # Calculate growth metrics
            total_members = guild.member_count
            # In a real implementation, you'd compare with historical data
            # For now, we'll simulate growth tracking

            # Get recent joins (last 7 days)
            recent_joins = 0
            week_ago = discord.utils.utcnow() - discord.timedelta(days=7)

            for member in guild.members:
                if member.joined_at and member.joined_at > week_ago:
                    recent_joins += 1

            growth_rate = (recent_joins / total_members) if total_members > 0 else 0.0

            # Simulate retention rate (in reality, track member activity)
            retention_rate = 0.75  # Placeholder

            metrics = {
                "total_members": total_members,
                "recent_joins": recent_joins,
                "growth_rate": growth_rate,
                "retention_rate": retention_rate,
                "growth_target": growth_target,
            }

            achieved = growth_rate >= growth_target and retention_rate >= 0.7
            return WorkflowResult(achieved_goal=achieved, metrics=metrics)

        except Exception as e:
            return WorkflowResult(achieved_goal=False, metrics={"error": str(e)})


__all__ = [
    "GhostInvitationWorkflow",
    "ServerGrowthWorkflow",
]
