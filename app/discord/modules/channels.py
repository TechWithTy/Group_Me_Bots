"""
Channel-related endpoints for Discord API.

This module implements all channel-related endpoints including CRUD operations,
permissions, and various channel types.
"""
import logging
from typing import List, Optional

import discord
from fastapi import APIRouter, HTTPException, Depends, Query
from discord.ext import commands

from .core import get_discord_client, DiscordAPIError, ResourceNotFound, check_rate_limit
from .models import (
    Channel, CreateChannelRequest, UpdateChannelRequest, DiscordObject,
    ChannelType, SnowflakeType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/channels", tags=["channels"])

@router.get("/{channel_id}", response_model=Channel)
async def get_channel(
    channel_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get channel information by ID."""
    check_rate_limit(f"get_channel:{channel_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        return Channel(
            id=discord_channel.id,
            type=ChannelType(discord_channel.type.name),
            name=getattr(discord_channel, 'name', None),
            position=getattr(discord_channel, 'position', None),
            parent_id=getattr(discord_channel, 'category_id', None),
            topic=getattr(discord_channel, 'topic', None),
            nsfw=getattr(discord_channel, 'nsfw', False),
            bitrate=getattr(discord_channel, 'bitrate', None),
            user_limit=getattr(discord_channel, 'user_limit', None),
            rate_limit_per_user=getattr(discord_channel, 'rate_limit_per_user', None),
            rtc_region=getattr(discord_channel, 'rtc_region', None),
            guild_id=discord_channel.guild.id if discord_channel.guild else None,
            last_message_id=getattr(discord_channel, 'last_message_id', None),
            default_auto_archive_duration=getattr(discord_channel, 'default_auto_archive_duration', None)
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/{channel_id}")
async def update_channel(
    channel_id: int,
    request: UpdateChannelRequest,
    client: commands.Bot = Depends(get_discord_client)
):
    """Update channel information."""
    check_rate_limit(f"update_channel:{channel_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        # Update channel properties
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.topic is not None:
            updates['topic'] = request.topic
        if request.nsfw is not None:
            updates['nsfw'] = request.nsfw
        if request.bitrate is not None:
            updates['bitrate'] = request.bitrate
        if request.user_limit is not None:
            updates['user_limit'] = request.user_limit
        if request.rate_limit_per_user is not None:
            updates['rate_limit_per_user'] = request.rate_limit_per_user

        if updates:
            await discord_channel.edit(**updates)

        return {"message": "Channel updated successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error updating channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update channel")

@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Delete a channel."""
    check_rate_limit(f"delete_channel:{channel_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        await discord_channel.delete()
        return {"message": "Channel deleted successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error deleting channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete channel")

@router.get("", response_model=List[Channel])
async def list_channels(
    guild_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """List channels in a guild."""
    check_rate_limit(f"list_channels:{guild_id}")

    try:
        guild = client.get_guild(guild_id)
        if not guild:
            raise ResourceNotFound("Guild", str(guild_id))

        channels = []
        for discord_channel in guild.channels:
            channels.append(Channel(
                id=discord_channel.id,
                type=ChannelType(discord_channel.type.name),
                name=getattr(discord_channel, 'name', None),
                position=getattr(discord_channel, 'position', None),
                parent_id=getattr(discord_channel, 'category_id', None),
                guild_id=guild_id
            ))

        return channels
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error listing channels for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("", response_model=Channel)
async def create_channel(
    request: CreateChannelRequest,
    client: commands.Bot = Depends(get_discord_client)
):
    """Create a new channel in a guild."""
    check_rate_limit(f"create_channel:{request.name}")

    try:
        guild = client.get_guild(request.guild_id if hasattr(request, 'guild_id') else 0)
        if not guild:
            raise ResourceNotFound("Guild", str(request.guild_id if hasattr(request, 'guild_id') else 0))

        # Map channel type to discord.py type
        channel_type_map = {
            ChannelType.GUILD_TEXT: "text",
            ChannelType.GUILD_VOICE: "voice",
            ChannelType.GUILD_CATEGORY: "category",
        }

        discord_type = channel_type_map.get(request.type, "text")

        # Create channel
        discord_channel = await guild.create_channel(
            name=request.name,
            type=getattr(discord, f"ChannelType.{discord_type}", discord.ChannelType.text),
            topic=request.topic,
            bitrate=request.bitrate,
            user_limit=request.user_limit,
            rate_limit_per_user=request.rate_limit_per_user,
            position=request.position,
            permission_overwrites=request.permission_overwrites,
            parent_id=request.parent_id,
            nsfw=request.nsfw
        )

        return Channel(
            id=discord_channel.id,
            type=ChannelType(discord_channel.type.name),
            name=discord_channel.name,
            position=discord_channel.position,
            parent_id=getattr(discord_channel, 'category_id', None),
            topic=getattr(discord_channel, 'topic', None),
            nsfw=getattr(discord_channel, 'nsfw', False),
            bitrate=getattr(discord_channel, 'bitrate', None),
            user_limit=getattr(discord_channel, 'user_limit', None),
            rate_limit_per_user=getattr(discord_channel, 'rate_limit_per_user', None),
            guild_id=guild.id
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error creating channel: {e}")
        raise HTTPException(status_code=500, detail="Failed to create channel")

