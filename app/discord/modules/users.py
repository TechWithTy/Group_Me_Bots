"""
User-related endpoints for Discord API.

This module implements all user-related endpoints including user information,
relationships, and user-specific operations.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from discord.ext import commands

from .core import get_discord_client, DiscordAPIError, ResourceNotFound, check_rate_limit
from .models import User, SnowflakeType, Connection

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/@me", response_model=User)
async def get_current_user(
    client: commands.Bot = Depends(get_discord_client)
):
    """Get current user information."""
    check_rate_limit("get_current_user")

    try:
        user = client.user
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")

        return User(
            id=user.id,
            username=user.name,
            discriminator=user.discriminator,
            avatar=user.avatar,
            bot=True,  # Bot accounts are always bots
            system=False,
            mfa_enabled=False,  # Bots don't have MFA
            verified=True  # Bots are verified by default
        )
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get user information by ID."""
    check_rate_limit(f"get_user:{user_id}")

    try:
        user = client.get_user(user_id)
        if not user:
            # Try to fetch from API if not in cache
            try:
                user = await client.fetch_user(user_id)
            except:
                raise ResourceNotFound("User", str(user_id))

        return User(
            id=user.id,
            username=user.name,
            discriminator=user.discriminator,
            avatar=user.avatar,
            bot=getattr(user, 'bot', False),
            system=getattr(user, 'system', False),
            mfa_enabled=False,
            verified=True
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}/profile", response_model=dict)
async def get_user_profile(
    user_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get user profile information."""
    check_rate_limit(f"get_user_profile:{user_id}")

    try:
        user = await client.fetch_user(user_id)

        # Get additional profile information
        profile_data = {
            "user": User(
                id=user.id,
                username=user.name,
                discriminator=user.discriminator,
                avatar=user.avatar,
                bot=getattr(user, 'bot', False)
            ),
            "connected_accounts": [],  # Would need to fetch from Discord API
            "premium_guild_since": None,  # Would need to fetch from Discord API
            "premium_since": None,  # Would need to fetch from Discord API
            "mutual_guilds": [],  # Would need to fetch from Discord API
            "guild_member": None  # Would need guild context
        }

        return profile_data
    except Exception as e:
        logger.error(f"Error getting profile for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/@me/guilds", response_model=List[dict])
async def get_current_user_guilds(
    before: Optional[int] = None,
    after: Optional[int] = None,
    limit: int = Query(200, ge=1, le=200),
    with_counts: bool = Query(False),
    client: commands.Bot = Depends(get_discord_client)
):
    """Get current user's guilds."""
    check_rate_limit("get_current_user_guilds")

    try:
        guilds = []
        for guild in client.guilds:
            if before and guild.id <= before:
                continue
            if after and guild.id <= after:
                continue

            guild_data = {
                "id": guild.id,
                "name": guild.name,
                "icon": guild.icon,
                "owner": guild.owner_id == client.user.id,
                "permissions": "0",  # Would need to calculate actual permissions
                "features": [str(f) for f in guild.features]
            }

            if with_counts:
                guild_data["approximate_member_count"] = guild.approximate_member_count
                guild_data["approximate_presence_count"] = guild.approximate_presence_count

            guilds.append(guild_data)

            if len(guilds) >= limit:
                break

        return guilds
    except Exception as e:
        logger.error(f"Error getting current user guilds: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{user_id}/connections", response_model=List[Connection])
async def get_user_connections(
    user_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get user connections (requires OAuth2)."""
    check_rate_limit(f"get_user_connections:{user_id}")

    try:
        # This would require OAuth2 authentication and Discord API calls
        # For now, return empty list as discord.py doesn't expose this
        return []
    except Exception as e:
        logger.error(f"Error getting connections for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/@me/channels", response_model=List[dict])
async def get_current_user_channels(
    client: commands.Bot = Depends(get_discord_client)
):
    """Get current user's DM channels."""
    check_rate_limit("get_current_user_channels")

    try:
        channels = []
        for channel in client.private_channels:
            if channel.type == discord.ChannelType.private:
                channel_data = {
                    "id": channel.id,
                    "type": channel.type.value,
                    "recipients": [
                        {
                            "id": recipient.id,
                            "username": recipient.name,
                            "discriminator": recipient.discriminator,
                            "avatar": recipient.avatar
                        } for recipient in channel.recipients
                    ],
                    "last_message_id": getattr(channel, 'last_message_id', None)
                }
                channels.append(channel_data)

        return channels
    except Exception as e:
        logger.error(f"Error getting current user channels: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/@me/channels", response_model=dict)
async def create_dm(
    recipient_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Create a DM channel with a user."""
    check_rate_limit(f"create_dm:{recipient_id}")

    try:
        user = client.get_user(recipient_id)
        if not user:
            raise ResourceNotFound("User", str(recipient_id))

        channel = await user.create_dm()

        return {
            "id": channel.id,
            "type": channel.type.value,
            "recipients": [
                {
                    "id": recipient.id,
                    "username": recipient.name,
                    "discriminator": recipient.discriminator,
                    "avatar": recipient.avatar
                } for recipient in channel.recipients
            ]
        }
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error creating DM with user {recipient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create DM")

@router.get("/@me/relationships", response_model=List[dict])
async def get_current_user_relationships(
    client: commands.Bot = Depends(get_discord_client)
):
    """Get current user's relationships (friends)."""
    check_rate_limit("get_current_user_relationships")

    try:
        # discord.py doesn't expose relationships
        # This would require Discord API calls
        return []
    except Exception as e:
        logger.error(f"Error getting current user relationships: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/@me/applications", response_model=List[dict])
async def get_current_user_applications(
    client: commands.Bot = Depends(get_discord_client)
):
    """Get current user's applications."""
    check_rate_limit("get_current_user_applications")

    try:
        # This would fetch from Discord's API
        return [
            {
                "id": str(client.user.id),
                "name": client.user.name,
                "icon": client.user.avatar,
                "description": "Discord Bot",
                "summary": "",
                "bot": {
                    "id": str(client.user.id),
                    "username": client.user.name,
                    "discriminator": client.user.discriminator,
                    "avatar": client.user.avatar
                }
            }
        ]
    except Exception as e:
        logger.error(f"Error getting current user applications: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
