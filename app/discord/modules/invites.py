"""Invite-related endpoints for Discord API."""
import logging
from typing import List

from fastapi import APIRouter, Depends
from discord.ext import commands

from .core import ResourceNotFound, check_rate_limit, get_discord_client
from .models import CreateChannelInviteRequest, Invite, Channel, ChannelType, discord_user_to_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["invites"])


def _convert_channel(discord_channel) -> Channel:
    if not discord_channel:
        return None

    channel_type = getattr(discord_channel, "type", None)
    type_name = getattr(channel_type, "name", ChannelType.GUILD_TEXT)
    try:
        resolved_type = ChannelType(str(type_name))
    except ValueError:
        resolved_type = ChannelType.GUILD_TEXT

    return Channel(
        id=discord_channel.id,
        type=resolved_type,
        name=getattr(discord_channel, "name", None),
        position=getattr(discord_channel, "position", None),
        parent_id=getattr(discord_channel, "parent_id", None),
    )


def _convert_invite(discord_invite) -> Invite:
    inviter = None
    if getattr(discord_invite, "inviter", None):
        inviter = discord_user_to_user(discord_invite.inviter)

    return Invite(
        code=discord_invite.code,
        guild=None,
        channel=_convert_channel(getattr(discord_invite, "channel", None)),
        inviter=inviter,
        target_type=getattr(discord_invite, "target_type", None),
        target_user=None,
        target_application=None,
        approximate_presence_count=getattr(discord_invite, "approximate_presence_count", None),
        approximate_member_count=getattr(discord_invite, "approximate_member_count", None),
        expires_at=getattr(discord_invite, "expires_at", None),
        stage_instance=getattr(discord_invite, "stage_instance", None),
        guild_scheduled_event=getattr(discord_invite, "guild_scheduled_event", None),
        uses=getattr(discord_invite, "uses", 0),
        max_uses=getattr(discord_invite, "max_uses", 0),
        max_age=getattr(discord_invite, "max_age", 0),
        temporary=getattr(discord_invite, "temporary", False),
        created_at=getattr(discord_invite, "created_at", None),
    )


async def _get_channel(client: commands.Bot, channel_id: int):
    channel = client.get_channel(channel_id)
    if not channel:
        raise ResourceNotFound("Channel", str(channel_id))
    return channel


@router.get("/channels/{channel_id}/invites", response_model=List[Invite])
async def get_channel_invites(
    channel_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> List[Invite]:
    """Get invites for a channel."""
    check_rate_limit(f"get_channel_invites:{channel_id}")

    channel = await _get_channel(client, channel_id)
    invites = await channel.invites()
    return [_convert_invite(invite) for invite in invites]


@router.post("/channels/{channel_id}/invites", response_model=Invite)
async def create_channel_invite(
    channel_id: int,
    request: CreateChannelInviteRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> Invite:
    """Create an invite for a channel."""
    check_rate_limit(f"create_invite:{channel_id}")

    channel = await _get_channel(client, channel_id)
    invite = await channel.create_invite(
        max_age=request.max_age,
        max_uses=request.max_uses,
        temporary=request.temporary,
        unique=request.unique,
        target_type=request.target_type,
        target_user=request.target_user_id,
        target_application=request.target_application_id,
    )
    return _convert_invite(invite)


@router.get("/guilds/{guild_id}/invites", response_model=List[Invite])
async def get_guild_invites(
    guild_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> List[Invite]:
    """Get invites for a guild."""
    check_rate_limit(f"get_guild_invites:{guild_id}")

    guild = client.get_guild(guild_id)
    if not guild:
        raise ResourceNotFound("Guild", str(guild_id))

    invites = await guild.invites()
    return [_convert_invite(invite) for invite in invites]


@router.get("/invites/{invite_code}", response_model=Invite)
async def get_invite(
    invite_code: str,
    client: commands.Bot = Depends(get_discord_client),
) -> Invite:
    """Get an invite by code."""
    check_rate_limit(f"get_invite:{invite_code}")

    invite = await client.fetch_invite(invite_code)
    return _convert_invite(invite)


@router.delete("/invites/{invite_code}")
async def delete_invite(
    invite_code: str,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Delete an invite by code."""
    check_rate_limit(f"delete_invite:{invite_code}")

    await client.delete_invite(invite_code)
    return {"message": "Invite deleted"}
