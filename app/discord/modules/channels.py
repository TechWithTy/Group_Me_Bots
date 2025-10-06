"""
Channel-related endpoints for Discord API.

This module implements all channel-related endpoints including CRUD operations,
permissions, and various channel types.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from discord.ext import commands

from .core import get_discord_client, DiscordAPIError, ResourceNotFound, check_rate_limit
from .models import (
    Channel, CreateChannelRequest, UpdateChannelRequest, DiscordObject,
    ChannelType, SnowflakeType, Message, CreateMessageRequest, EditMessageRequest
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

@router.get("/{channel_id}/messages", response_model=List[Message])
async def get_channel_messages(
    channel_id: int,
    limit: int = Query(50, ge=1, le=100),
    before: Optional[int] = None,
    after: Optional[int] = None,
    around: Optional[int] = None,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get messages from a channel."""
    check_rate_limit(f"get_messages:{channel_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        messages = []
        async for discord_message in discord_channel.history(
            limit=limit,
            before=discord.Object(id=before) if before else None,
            after=discord.Object(id=after) if after else None,
            around=discord.Object(id=around) if around else None
        ):
            # Convert discord.py message to API model
            message = Message(
                id=discord_message.id,
                channel_id=discord_message.channel.id,
                author=Message.Author(
                    id=discord_message.author.id,
                    username=discord_message.author.name,
                    discriminator=discord_message.author.discriminator,
                    avatar=getattr(discord_message.author, 'avatar', None),
                    bot=getattr(discord_message.author, 'bot', False)
                ) if hasattr(discord_message.author, 'name') else None,
                content=discord_message.content,
                timestamp=discord_message.created_at,
                edited_timestamp=discord_message.edited_at,
                tts=discord_message.tts,
                mention_everyone=discord_message.mention_everyone,
                pinned=discord_message.pinned,
                type=discord_message.type.value if hasattr(discord_message.type, 'value') else 0
            )
            messages.append(message)

        return messages
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@router.post("/{channel_id}/messages", response_model=Message)
async def create_message(
    channel_id: int,
    request: CreateMessageRequest,
    client: commands.Bot = Depends(get_discord_client)
):
    """Create a new message in a channel."""
    check_rate_limit(f"create_message:{channel_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        # Send message
        discord_message = await discord_channel.send(
            content=request.content,
            tts=request.tts,
            embeds=request.embeds,
            nonce=request.nonce
        )

        # Convert to API model
        message = Message(
            id=discord_message.id,
            channel_id=discord_message.channel.id,
            author=Message.Author(
                id=discord_message.author.id,
                username=discord_message.author.name,
                discriminator=discord_message.author.discriminator,
                avatar=getattr(discord_message.author, 'avatar', None),
                bot=getattr(discord_message.author, 'bot', False)
            ) if hasattr(discord_message.author, 'name') else None,
            content=discord_message.content,
            timestamp=discord_message.created_at,
            edited_timestamp=discord_message.edited_at,
            tts=discord_message.tts,
            mention_everyone=discord_message.mention_everyone,
            pinned=discord_message.pinned,
            type=discord_message.type.value if hasattr(discord_message.type, 'value') else 0
        )

        return message
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error creating message in channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create message")

@router.get("/{channel_id}/messages/{message_id}", response_model=Message)
async def get_message(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get a specific message from a channel."""
    check_rate_limit(f"get_message:{channel_id}:{message_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        try:
            discord_message = await discord_channel.fetch_message(message_id)
        except discord.NotFound:
            raise ResourceNotFound("Message", str(message_id))

        # Convert to API model
        message = Message(
            id=discord_message.id,
            channel_id=discord_message.channel.id,
            author=Message.Author(
                id=discord_message.author.id,
                username=discord_message.author.name,
                discriminator=discord_message.author.discriminator,
                avatar=getattr(discord_message.author, 'avatar', None),
                bot=getattr(discord_message.author, 'bot', False)
            ) if hasattr(discord_message.author, 'name') else None,
            content=discord_message.content,
            timestamp=discord_message.created_at,
            edited_timestamp=discord_message.edited_at,
            tts=discord_message.tts,
            mention_everyone=discord_message.mention_everyone,
            pinned=discord_message.pinned,
            type=discord_message.type.value if hasattr(discord_message.type, 'value') else 0
        )

        return message
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting message {message_id} from channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get message")

@router.patch("/{channel_id}/messages/{message_id}")
async def edit_message(
    channel_id: int,
    message_id: int,
    request: EditMessageRequest,
    client: commands.Bot = Depends(get_discord_client)
):
    """Edit a message in a channel."""
    check_rate_limit(f"edit_message:{channel_id}:{message_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        try:
            discord_message = await discord_channel.fetch_message(message_id)
        except discord.NotFound:
            raise ResourceNotFound("Message", str(message_id))

        # Edit message
        await discord_message.edit(
            content=request.content,
            embeds=request.embeds
        )

        return {"message": "Message edited successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error editing message {message_id} in channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to edit message")

@router.delete("/{channel_id}/messages/{message_id}")
async def delete_message(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Delete a message from a channel."""
    check_rate_limit(f"delete_message:{channel_id}:{message_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        try:
            discord_message = await discord_channel.fetch_message(message_id)
        except discord.NotFound:
            raise ResourceNotFound("Message", str(message_id))

        await discord_message.delete()
        return {"message": "Message deleted successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error deleting message {message_id} from channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete message")

@router.post("/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
async def add_reaction(
    channel_id: int,
    message_id: int,
    emoji: str,
    client: commands.Bot = Depends(get_discord_client)
):
    """Add a reaction to a message."""
    check_rate_limit(f"add_reaction:{channel_id}:{message_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        try:
            discord_message = await discord_channel.fetch_message(message_id)
        except discord.NotFound:
            raise ResourceNotFound("Message", str(message_id))

        await discord_message.add_reaction(emoji)
        return {"message": "Reaction added successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error adding reaction to message {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add reaction")

@router.delete("/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
async def remove_reaction(
    channel_id: int,
    message_id: int,
    emoji: str,
    client: commands.Bot = Depends(get_discord_client)
):
    """Remove a reaction from a message."""
    check_rate_limit(f"remove_reaction:{channel_id}:{message_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        try:
            discord_message = await discord_channel.fetch_message(message_id)
        except discord.NotFound:
            raise ResourceNotFound("Message", str(message_id))

        await discord_message.remove_reaction(emoji, client.user)
        return {"message": "Reaction removed successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error removing reaction from message {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove reaction")

@router.post("/{channel_id}/messages/{message_id}/crosspost")
async def crosspost_message(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Crosspost a message in an announcement channel."""
    check_rate_limit(f"crosspost_message:{channel_id}:{message_id}")

    try:
        discord_channel = client.get_channel(channel_id)
        if not discord_channel:
            raise ResourceNotFound("Channel", str(channel_id))

        # Check if channel is an announcement channel
        if discord_channel.type != discord.ChannelType.news:
            raise HTTPException(
                status_code=400,
                detail="Channel must be an announcement channel"
            )

        try:
            discord_message = await discord_channel.fetch_message(message_id)
        except discord.NotFound:
            raise ResourceNotFound("Message", str(message_id))

        await discord_message.publish()
        return {"message": "Message crossposted successfully"}
    except ResourceNotFound:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error crossposting message {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to crosspost message")
