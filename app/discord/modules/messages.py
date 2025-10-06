"""Message-related endpoints for Discord API."""
import logging
from typing import List

import discord
from fastapi import APIRouter, Depends, HTTPException
from discord.ext import commands

from .core import ResourceNotFound, check_rate_limit, get_discord_client
from .models import (
    CreateMessageRequest,
    EditMessageRequest,
    Message,
    discord_message_to_message,
    discord_user_to_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["messages"])


async def _get_channel(client: commands.Bot, channel_id: int):
    channel = client.get_channel(channel_id)
    if not channel:
        raise ResourceNotFound("Channel", str(channel_id))
    return channel


async def _fetch_message(channel, message_id: int):
    try:
        return await channel.fetch_message(message_id)
    except discord.NotFound as exc:  # pragma: no cover - relies on discord internals
        raise ResourceNotFound("Message", str(message_id)) from exc


@router.get("/channels/{channel_id}/messages/{message_id}", response_model=Message)
async def get_message(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> Message:
    """Get a specific message from a channel."""
    check_rate_limit(f"get_message:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)
    return discord_message_to_message(discord_message)


@router.patch("/channels/{channel_id}/messages/{message_id}")
async def edit_message(
    channel_id: int,
    message_id: int,
    request: EditMessageRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Edit a message in a channel."""
    check_rate_limit(f"edit_message:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)

    await discord_message.edit(
        content=request.content,
        embeds=request.embeds,
        allowed_mentions=request.allowed_mentions,
        components=request.components,
        attachments=request.attachments,
        flags=request.flags,
    )
    return {"message": "Message edited successfully"}


@router.delete("/channels/{channel_id}/messages/{message_id}")
async def delete_message(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Delete a message from a channel."""
    check_rate_limit(f"delete_message:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)
    await discord_message.delete()
    return {"message": "Message deleted successfully"}


@router.put("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
async def add_reaction(
    channel_id: int,
    message_id: int,
    emoji: str,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Add the current user's reaction to a message."""
    check_rate_limit(f"add_reaction:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)
    await discord_message.add_reaction(emoji)
    return {"message": "Reaction added successfully"}


@router.delete("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")
async def remove_own_reaction(
    channel_id: int,
    message_id: int,
    emoji: str,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Remove the current user's reaction from a message."""
    check_rate_limit(f"remove_reaction:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)
    await discord_message.remove_reaction(emoji, client.user)
    return {"message": "Reaction removed successfully"}


@router.delete("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}")
async def remove_user_reaction(
    channel_id: int,
    message_id: int,
    emoji: str,
    user_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Remove another user's reaction from a message."""
    check_rate_limit(f"remove_user_reaction:{channel_id}:{message_id}:{user_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)

    user = client.get_user(user_id)
    if not user:
        try:
            user = await client.fetch_user(user_id)
        except discord.NotFound as exc:  # pragma: no cover - relies on discord internals
            raise ResourceNotFound("User", str(user_id)) from exc

    await discord_message.remove_reaction(emoji, user)
    return {"message": "Reaction removed successfully"}


@router.get("/channels/{channel_id}/messages/{message_id}/reactions")
async def list_reactions(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> List[dict]:
    """List reaction summaries for a message."""
    check_rate_limit(f"list_reactions:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)

    reactions = []
    for reaction in discord_message.reactions:
        reactions.append(
            {
                "emoji": str(reaction.emoji),
                "count": reaction.count,
                "me": reaction.me,
            }
        )
    return reactions


def _match_emoji(reaction, emoji: str) -> bool:
    if str(reaction.emoji) == emoji:
        return True
    emoji_name = getattr(reaction.emoji, "name", None)
    return emoji_name == emoji


@router.get("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")
async def get_reaction_users(
    channel_id: int,
    message_id: int,
    emoji: str,
    client: commands.Bot = Depends(get_discord_client),
) -> List[dict]:
    """Get users who reacted with a specific emoji."""
    check_rate_limit(f"get_reaction_users:{channel_id}:{message_id}:{emoji}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)

    target_reaction = None
    for reaction in discord_message.reactions:
        if _match_emoji(reaction, emoji):
            target_reaction = reaction
            break

    if not target_reaction:
        raise ResourceNotFound("Reaction", emoji)

    users = await target_reaction.users()
    user_list = []
    if isinstance(users, list):
        iterable = users
    else:  # pragma: no cover - depends on discord implementation
        iterable = []
        async for user in users:
            iterable.append(user)

    for user in iterable:
        user_list.append(discord_user_to_user(user).dict())
    return user_list


@router.post("/channels/{channel_id}/messages/{message_id}/crosspost")
async def crosspost_message(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Crosspost a message from a news channel."""
    check_rate_limit(f"crosspost:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    channel_type = getattr(channel, "type", None)
    is_news_channel = False
    if isinstance(channel_type, discord.ChannelType):
        is_news_channel = channel_type == discord.ChannelType.news
    elif hasattr(channel_type, "name"):
        is_news_channel = str(channel_type.name).lower() == "news"

    if not is_news_channel:
        raise HTTPException(status_code=400, detail="Channel must be an announcement channel")

    discord_message = await _fetch_message(channel, message_id)
    await discord_message.publish()
    return {"message": "Message crossposted successfully"}


@router.post("/channels/{channel_id}/messages/{message_id}/suppress-embeds")
async def suppress_embeds(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Suppress embeds for a message."""
    check_rate_limit(f"suppress_embeds:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)
    await discord_message.edit(suppress=True)
    return {"message": "Embeds suppressed"}


@router.delete("/channels/{channel_id}/messages/{message_id}/suppress-embeds")
async def unsuppress_embeds(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Remove embed suppression from a message."""
    check_rate_limit(f"unsuppress_embeds:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)
    await discord_message.edit(suppress=False)
    return {"message": "Embeds unsuppressed"}


@router.put("/channels/{channel_id}/pins/{message_id}")
async def pin_message(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Pin a message."""
    check_rate_limit(f"pin_message:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)
    await discord_message.pin()
    return {"message": "Message pinned"}


@router.delete("/channels/{channel_id}/pins/{message_id}")
async def unpin_message(
    channel_id: int,
    message_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Unpin a message."""
    check_rate_limit(f"unpin_message:{channel_id}:{message_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await _fetch_message(channel, message_id)
    await discord_message.unpin()
    return {"message": "Message unpinned"}


@router.get("/channels/{channel_id}/pins", response_model=List[Message])
async def get_pinned_messages(
    channel_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> List[Message]:
    """Get pinned messages from a channel."""
    check_rate_limit(f"get_pins:{channel_id}")

    channel = await _get_channel(client, channel_id)
    pinned = await channel.pins()
    return [discord_message_to_message(message) for message in pinned]


@router.post("/channels/{channel_id}/messages", response_model=Message)
async def create_message(
    channel_id: int,
    request: CreateMessageRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> Message:
    """Create a new message in a channel."""
    check_rate_limit(f"create_message:{channel_id}")

    channel = await _get_channel(client, channel_id)
    discord_message = await channel.send(
        content=request.content,
        tts=request.tts,
        embeds=request.embeds,
        nonce=request.nonce,
        allowed_mentions=request.allowed_mentions,
        components=request.components,
        stickers=request.sticker_ids,
    )
    return discord_message_to_message(discord_message)
