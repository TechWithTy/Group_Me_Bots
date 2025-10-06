"""Interaction-related endpoints for Discord API."""
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from discord.ext import commands

from .core import check_rate_limit, get_discord_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["interactions"])


class InteractionCallback(BaseModel):
    """Model representing an interaction callback payload."""
    type: int = Field(..., description="Interaction callback type")
    data: Dict[str, Any] = Field(default_factory=dict)


class CommandPermissionsUpdate(BaseModel):
    """Model representing command permissions update payload."""
    permissions: List[Dict[str, Any]]


@router.post("/interactions", response_model=InteractionCallback)
async def create_interaction_response(
    callback: InteractionCallback,
    client: commands.Bot = Depends(get_discord_client),
) -> InteractionCallback:
    """Create an interaction response."""
    check_rate_limit("create_interaction_response")

    # Real implementation would forward the response to Discord's interactions API.
    # For now we simply echo the payload.
    return callback


@router.get("/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions")
async def get_command_permissions(
    application_id: int,
    guild_id: int,
    command_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> Dict[str, Any]:
    """Get command permissions for a guild command."""
    check_rate_limit(f"get_command_permissions:{application_id}:{guild_id}:{command_id}")

    if not getattr(client, "http", None):
        return {"permissions": []}

    return await client.http.get_guild_command_permissions(application_id, guild_id, command_id)


@router.put("/applications/{application_id}/guilds/{guild_id}/commands/{command_id}/permissions")
async def set_command_permissions(
    application_id: int,
    guild_id: int,
    command_id: int,
    request: CommandPermissionsUpdate,
    client: commands.Bot = Depends(get_discord_client),
) -> Dict[str, Any]:
    """Set command permissions for a guild command."""
    check_rate_limit(f"set_command_permissions:{application_id}:{guild_id}:{command_id}")

    if not getattr(client, "http", None):
        return {"permissions": request.permissions}

    return await client.http.put_guild_command_permissions(
        application_id,
        guild_id,
        command_id,
        request.permissions,
    )
