"""
Guild-related endpoints for Discord API.

This module implements all guild-related endpoints including members, roles,
bans, and other guild management operations.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from discord.ext import commands

from .core import get_discord_client, DiscordAPIError, ResourceNotFound, check_rate_limit
from .models import (
    Guild, User, Role, CreateGuildRequest, CreateRoleRequest, UpdateRoleRequest,
    SnowflakeType, Ban, VoiceState, VoiceRegion, GuildMember
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/guilds", tags=["guilds"])

@router.get("/{guild_id}", response_model=Guild)
async def get_guild(
    guild_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get guild information by ID."""
    check_rate_limit(f"get_guild:{guild_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        return Guild(
            id=discord_guild.id,
            name=discord_guild.name,
            icon=discord_guild.icon,
            owner_id=discord_guild.owner_id,
            region=discord_guild.region,
            afk_channel_id=discord_guild.afk_channel.id if discord_guild.afk_channel else None,
            afk_timeout=discord_guild.afk_timeout,
            verification_level=discord_guild.verification_level.value,
            default_message_notifications=discord_guild.default_notifications.value,
            explicit_content_filter=discord_guild.explicit_content_filter,
            features=[str(f) for f in discord_guild.features],
            mfa_level=discord_guild.mfa_level,
            system_channel_id=discord_guild.system_channel.id if discord_guild.system_channel else None,
            rules_channel_id=discord_guild.rules_channel.id if discord_guild.rules_channel else None,
            max_presences=discord_guild.max_presences,
            vanity_url_code=discord_guild.vanity_url_code,
            description=discord_guild.description,
            banner=discord_guild.banner,
            premium_tier=discord_guild.premium_tier,
            preferred_locale=str(discord_guild.preferred_locale),
            public_updates_channel_id=discord_guild.public_updates_channel.id if discord_guild.public_updates_channel else None,
            max_video_channel_users=discord_guild.max_video_channel_users,
            approximate_member_count=discord_guild.approximate_member_count,
            approximate_presence_count=discord_guild.approximate_presence_count,
            nsfw_level=discord_guild.nsfw_level,
            premium_progress_bar_enabled=discord_guild.premium_progress_bar_enabled
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{guild_id}/members", response_model=List[GuildMember])
async def list_guild_members(
    guild_id: int,
    limit: int = Query(1000, ge=1, le=1000),
    after: Optional[int] = None,
    client: commands.Bot = Depends(get_discord_client)
):
    """List guild members."""
    check_rate_limit(f"list_members:{guild_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        members = []
        async for discord_member in discord_guild.fetch_members(limit=limit):
            if after and discord_member.id <= after:
                continue

            member = GuildMember(
                user=User(
                    id=discord_member.id,
                    username=discord_member.name,
                    discriminator=discord_member.discriminator,
                    avatar=discord_member.avatar,
                    bot=getattr(discord_member, 'bot', False)
                ),
                nick=discord_member.nick,
                avatar=discord_member.avatar,
                roles=[role.id for role in discord_member.roles],
                joined_at=discord_member.joined_at,
                premium_since=discord_member.premium_since,
                deaf=discord_member.voice.deaf if discord_member.voice else False,
                mute=discord_member.voice.mute if discord_member.voice else False,
                pending=discord_member.pending,
                permissions=str(discord_member.guild_permissions.value) if discord_member.guild_permissions else "0"
            )
            members.append(member)

            if len(members) >= limit:
                break

        return members
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error listing members for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{guild_id}/members/{user_id}", response_model=GuildMember)
async def get_guild_member(
    guild_id: int,
    user_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get a specific guild member."""
    check_rate_limit(f"get_member:{guild_id}:{user_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        try:
            discord_member = await discord_guild.fetch_member(user_id)
        except discord.NotFound:
            raise ResourceNotFound("Member", str(user_id))

        return GuildMember(
            user=User(
                id=discord_member.id,
                username=discord_member.name,
                discriminator=discord_member.discriminator,
                avatar=discord_member.avatar,
                bot=getattr(discord_member, 'bot', False)
            ),
            nick=discord_member.nick,
            avatar=discord_member.avatar,
            roles=[role.id for role in discord_member.roles],
            joined_at=discord_member.joined_at,
            premium_since=discord_member.premium_since,
            deaf=discord_member.voice.deaf if discord_member.voice else False,
            mute=discord_member.voice.mute if discord_member.voice else False,
            pending=discord_member.pending,
            permissions=str(discord_member.guild_permissions.value) if discord_member.guild_permissions else "0"
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting member {user_id} from guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get member")

@router.get("/{guild_id}/roles", response_model=List[Role])
async def list_guild_roles(
    guild_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """List guild roles."""
    check_rate_limit(f"list_roles:{guild_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        roles = []
        for discord_role in discord_guild.roles:
            role = Role(
                id=discord_role.id,
                name=discord_role.name,
                color=discord_role.color,
                hoist=discord_role.hoist,
                icon=discord_role.icon,
                unicode_emoji=discord_role.unicode_emoji,
                position=discord_role.position,
                permissions=str(discord_role.permissions.value),
                managed=discord_role.managed,
                mentionable=discord_role.mentionable,
                tags=discord_role.tags,
                flags=discord_role.flags
            )
            roles.append(role)

        return roles
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error listing roles for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{guild_id}/roles", response_model=Role)
async def create_guild_role(
    guild_id: int,
    request: CreateRoleRequest,
    client: commands.Bot = Depends(get_discord_client)
):
    """Create a new guild role."""
    check_rate_limit(f"create_role:{guild_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        discord_role = await discord_guild.create_role(
            name=request.name,
            permissions=discord.Permissions(int(request.permissions or "0")),
            color=request.color or 0,
            hoist=request.hoist or False,
            mentionable=request.mentionable or False
        )

        return Role(
            id=discord_role.id,
            name=discord_role.name,
            color=discord_role.color,
            hoist=discord_role.hoist,
            position=discord_role.position,
            permissions=str(discord_role.permissions.value),
            managed=discord_role.managed,
            mentionable=discord_role.mentionable
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error creating role in guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create role")

@router.patch("/{guild_id}/roles/{role_id}", response_model=Role)
async def update_guild_role(
    guild_id: int,
    role_id: int,
    request: UpdateRoleRequest,
    client: commands.Bot = Depends(get_discord_client)
):
    """Update a guild role."""
    check_rate_limit(f"update_role:{guild_id}:{role_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        discord_role = discord_guild.get_role(role_id)
        if not discord_role:
            raise ResourceNotFound("Role", str(role_id))

        # Update role properties
        updates = {}
        if request.name is not None:
            updates['name'] = request.name
        if request.permissions is not None:
            updates['permissions'] = discord.Permissions(int(request.permissions))
        if request.color is not None:
            updates['color'] = request.color
        if request.hoist is not None:
            updates['hoist'] = request.hoist
        if request.mentionable is not None:
            updates['mentionable'] = request.mentionable

        await discord_role.edit(**updates)

        return Role(
            id=discord_role.id,
            name=discord_role.name,
            color=discord_role.color,
            hoist=discord_role.hoist,
            position=discord_role.position,
            permissions=str(discord_role.permissions.value),
            managed=discord_role.managed,
            mentionable=discord_role.mentionable
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error updating role {role_id} in guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update role")

@router.delete("/{guild_id}/roles/{role_id}")
async def delete_guild_role(
    guild_id: int,
    role_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Delete a guild role."""
    check_rate_limit(f"delete_role:{guild_id}:{role_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        discord_role = discord_guild.get_role(role_id)
        if not discord_role:
            raise ResourceNotFound("Role", str(role_id))

        await discord_role.delete()
        return {"message": "Role deleted successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error deleting role {role_id} from guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete role")

@router.get("/{guild_id}/bans", response_model=List[Ban])
async def list_guild_bans(
    guild_id: int,
    limit: int = Query(1000, ge=1, le=1000),
    before: Optional[int] = None,
    after: Optional[int] = None,
    client: commands.Bot = Depends(get_discord_client)
):
    """List guild bans."""
    check_rate_limit(f"list_bans:{guild_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        bans = []
        async for ban_entry in discord_guild.bans(limit=limit):
            if before and ban_entry.user.id <= before:
                continue
            if after and ban_entry.user.id <= after:
                continue

            ban = Ban(
                reason=ban_entry.reason,
                user=User(
                    id=ban_entry.user.id,
                    username=ban_entry.user.name,
                    discriminator=ban_entry.user.discriminator,
                    avatar=ban_entry.user.avatar,
                    bot=getattr(ban_entry.user, 'bot', False)
                )
            )
            bans.append(ban)

        return bans
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error listing bans for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{guild_id}/bans/{user_id}", response_model=Ban)
async def get_guild_ban(
    guild_id: int,
    user_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get a specific guild ban."""
    check_rate_limit(f"get_ban:{guild_id}:{user_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        try:
            ban_entry = await discord_guild.fetch_ban(user_id)
        except discord.NotFound:
            raise ResourceNotFound("Ban", str(user_id))

        return Ban(
            reason=ban_entry.reason,
            user=User(
                id=ban_entry.user.id,
                username=ban_entry.user.name,
                discriminator=ban_entry.user.discriminator,
                avatar=ban_entry.user.avatar,
                bot=getattr(ban_entry.user, 'bot', False)
            )
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting ban for user {user_id} in guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get ban")

@router.put("/{guild_id}/bans/{user_id}")
async def create_guild_ban(
    guild_id: int,
    user_id: int,
    delete_message_days: int = Query(0, ge=0, le=7),
    reason: Optional[str] = Query(None, max_length=512),
    client: commands.Bot = Depends(get_discord_client)
):
    """Create a guild ban."""
    check_rate_limit(f"create_ban:{guild_id}:{user_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        user = client.get_user(user_id)
        if not user:
            raise ResourceNotFound("User", str(user_id))

        await discord_guild.ban(
            user,
            reason=reason,
            delete_message_days=delete_message_days
        )

        return {"message": "User banned successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error banning user {user_id} in guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to ban user")

@router.delete("/{guild_id}/bans/{user_id}")
async def remove_guild_ban(
    guild_id: int,
    user_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Remove a guild ban."""
    check_rate_limit(f"remove_ban:{guild_id}:{user_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        user = client.get_user(user_id)
        if not user:
            raise ResourceNotFound("User", str(user_id))

        await discord_guild.unban(user)
        return {"message": "User unbanned successfully"}
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error unbanning user {user_id} in guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to unban user")

@router.get("/{guild_id}/voice-states", response_model=List[VoiceState])
async def list_voice_states(
    guild_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """List voice states in a guild."""
    check_rate_limit(f"list_voice_states:{guild_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        voice_states = []
        for voice_state in discord_guild.voice_states.values():
            state = VoiceState(
                channel_id=voice_state.channel.id if voice_state.channel else None,
                user_id=voice_state.user_id,
                session_id=voice_state.session_id,
                deaf=voice_state.deaf,
                mute=voice_state.mute,
                self_deaf=voice_state.self_deaf,
                self_mute=voice_state.self_mute,
                self_stream=voice_state.self_stream,
                self_video=voice_state.self_video,
                suppress=voice_state.suppress
            )
            voice_states.append(state)

        return voice_states
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error listing voice states for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{guild_id}/voice-states/{user_id}", response_model=VoiceState)
async def get_voice_state(
    guild_id: int,
    user_id: int,
    client: commands.Bot = Depends(get_discord_client)
):
    """Get a specific voice state."""
    check_rate_limit(f"get_voice_state:{guild_id}:{user_id}")

    try:
        discord_guild = client.get_guild(guild_id)
        if not discord_guild:
            raise ResourceNotFound("Guild", str(guild_id))

        voice_state = discord_guild.voice_states.get(user_id)
        if not voice_state:
            raise ResourceNotFound("Voice State", str(user_id))

        return VoiceState(
            channel_id=voice_state.channel.id if voice_state.channel else None,
            user_id=voice_state.user_id,
            session_id=voice_state.session_id,
            deaf=voice_state.deaf,
            mute=voice_state.mute,
            self_deaf=voice_state.self_deaf,
            self_mute=voice_state.self_mute,
            self_stream=voice_state.self_stream,
            self_video=voice_state.self_video,
            suppress=voice_state.suppress
        )
    except ResourceNotFound:
        raise
    except Exception as e:
        logger.error(f"Error getting voice state for user {user_id} in guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice state")
