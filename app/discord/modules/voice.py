"""Voice-related endpoints for Discord API."""
import logging
from typing import List

from fastapi import APIRouter, Depends
from discord.ext import commands

from .core import ResourceNotFound, check_rate_limit, get_discord_client
from .models import UpdateVoiceStateRequest, VoiceRegion, VoiceState

logger = logging.getLogger(__name__)

router = APIRouter(tags=["voice"])


@router.get("/voice/regions", response_model=List[VoiceRegion])
async def get_voice_regions(client: commands.Bot = Depends(get_discord_client)) -> List[VoiceRegion]:
    """Get available voice regions."""
    check_rate_limit("get_voice_regions")

    if not getattr(client, "http", None):
        return []

    regions = await client.http.get_voice_regions()
    return [VoiceRegion(**region) for region in regions]


@router.get("/guilds/{guild_id}/voice-states/{user_id}", response_model=VoiceState)
async def get_voice_state(
    guild_id: int,
    user_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> VoiceState:
    """Get a user's voice state in a guild."""
    check_rate_limit(f"get_voice_state:{guild_id}:{user_id}")

    guild = client.get_guild(guild_id)
    if not guild:
        raise ResourceNotFound("Guild", str(guild_id))

    member = guild.get_member(user_id)
    if not member:
        member = await guild.fetch_member(user_id)

    if not getattr(member, "voice", None):
        raise ResourceNotFound("VoiceState", str(user_id))

    voice = member.voice
    return VoiceState(
        channel_id=getattr(voice.channel, "id", None),
        user_id=getattr(voice, "user_id", member.id),
        session_id=getattr(voice, "session_id", ""),
        deaf=getattr(voice, "deaf", False),
        mute=getattr(voice, "mute", False),
        self_deaf=getattr(voice, "self_deaf", False),
        self_mute=getattr(voice, "self_mute", False),
        self_stream=getattr(voice, "self_stream", False),
        self_video=getattr(voice, "self_video", False),
        suppress=getattr(voice, "suppress", False),
        request_to_speak_timestamp=getattr(voice, "request_to_speak_timestamp", None),
    )


@router.patch("/guilds/{guild_id}/voice-states/@me")
async def update_my_voice_state(
    guild_id: int,
    request: UpdateVoiceStateRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Update the current user's voice state."""
    check_rate_limit(f"update_voice_state:{guild_id}")

    guild = client.get_guild(guild_id)
    if not guild:
        raise ResourceNotFound("Guild", str(guild_id))

    await guild.change_voice_state(
        channel=request.channel_id,
        self_mute=request.self_mute,
        self_deaf=request.self_deaf,
        suppress=request.suppress,
        request_to_speak=request.request_to_speak_timestamp,
    )
    return {"message": "Voice state updated"}
