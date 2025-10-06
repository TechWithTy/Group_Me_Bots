"""Webhook-related endpoints for Discord API."""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends
from discord.ext import commands

from .core import ResourceNotFound, check_rate_limit, get_discord_client
from .models import (
    CreateWebhookRequest,
    EditWebhookMessageRequest,
    ExecuteWebhookRequest,
    UpdateWebhookRequest,
    Webhook,
    discord_user_to_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhooks"])


def _convert_webhook(discord_webhook) -> Webhook:
    user = None
    if getattr(discord_webhook, "user", None):
        user = discord_user_to_user(discord_webhook.user)

    def _safe_attr(name: str, expected_type=str):
        value = getattr(discord_webhook, name, None)
        if value is None:
            return None
        if isinstance(value, expected_type):
            return value
        if expected_type is int:
            try:
                return int(value)
            except (TypeError, ValueError):
                return None
        return str(value)

    type_attr = getattr(discord_webhook, "type", 1)
    if hasattr(type_attr, "value"):
        type_attr = getattr(type_attr, "value")
    try:
        webhook_type = int(type_attr)
    except (TypeError, ValueError):
        webhook_type = 1

    return Webhook(
        id=discord_webhook.id,
        type=webhook_type,
        guild_id=_safe_attr("guild_id", int),
        channel_id=_safe_attr("channel_id", int),
        user=user,
        name=_safe_attr("name"),
        avatar=_safe_attr("avatar"),
        token=_safe_attr("token"),
        application_id=_safe_attr("application_id", int),
        source_guild=None,
        source_channel=None,
        url=_safe_attr("url"),
    )


async def _get_channel(client: commands.Bot, channel_id: int):
    channel = client.get_channel(channel_id)
    if not channel:
        raise ResourceNotFound("Channel", str(channel_id))
    return channel


@router.get("/channels/{channel_id}/webhooks", response_model=List[Webhook])
async def get_channel_webhooks(
    channel_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> List[Webhook]:
    """Get webhooks for a specific channel."""
    check_rate_limit(f"get_channel_webhooks:{channel_id}")

    channel = await _get_channel(client, channel_id)
    hooks = await channel.webhooks()
    return [_convert_webhook(webhook) for webhook in hooks]


@router.post("/channels/{channel_id}/webhooks", response_model=Webhook)
async def create_channel_webhook(
    channel_id: int,
    request: CreateWebhookRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> Webhook:
    """Create a new webhook in a channel."""
    check_rate_limit(f"create_webhook:{channel_id}")

    channel = await _get_channel(client, channel_id)
    webhook = await channel.create_webhook(name=request.name, avatar=request.avatar, reason=None)
    return _convert_webhook(webhook)


@router.get("/guilds/{guild_id}/webhooks", response_model=List[Webhook])
async def get_guild_webhooks(
    guild_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> List[Webhook]:
    """Get all webhooks for a guild."""
    check_rate_limit(f"get_guild_webhooks:{guild_id}")

    guild = client.get_guild(guild_id)
    if not guild:
        raise ResourceNotFound("Guild", str(guild_id))

    hooks = await guild.webhooks()
    return [_convert_webhook(webhook) for webhook in hooks]


@router.get("/webhooks/{webhook_id}", response_model=Webhook)
async def get_webhook(
    webhook_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> Webhook:
    """Get a webhook by ID."""
    check_rate_limit(f"get_webhook:{webhook_id}")

    webhook = await client.fetch_webhook(webhook_id)
    return _convert_webhook(webhook)


@router.get("/webhooks/{webhook_id}/{webhook_token}", response_model=Webhook)
async def get_webhook_with_token(
    webhook_id: int,
    webhook_token: str,
    client: commands.Bot = Depends(get_discord_client),
) -> Webhook:
    """Get a webhook using its token."""
    check_rate_limit(f"get_webhook_token:{webhook_id}")

    webhook = await client.fetch_webhook(webhook_id, webhook_token)
    return _convert_webhook(webhook)


@router.patch("/webhooks/{webhook_id}", response_model=Webhook)
async def update_webhook(
    webhook_id: int,
    request: UpdateWebhookRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> Webhook:
    """Update a webhook."""
    check_rate_limit(f"update_webhook:{webhook_id}")

    webhook = await client.fetch_webhook(webhook_id)
    updated = await webhook.edit(name=request.name, avatar=request.avatar, channel=request.channel_id)
    if request.name is not None:
        setattr(updated, "name", request.name)
    if request.avatar is not None:
        setattr(updated, "avatar", request.avatar)
    if request.channel_id is not None:
        setattr(updated, "channel_id", request.channel_id)
    return _convert_webhook(updated)


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Delete a webhook."""
    check_rate_limit(f"delete_webhook:{webhook_id}")

    webhook = await client.fetch_webhook(webhook_id)
    await webhook.delete()
    return {"message": "Webhook deleted successfully"}


async def _fetch_webhook_with_token(
    client: commands.Bot,
    webhook_id: int,
    webhook_token: str,
):
    webhook = await client.fetch_webhook(webhook_id, webhook_token)
    return webhook


@router.post("/webhooks/{webhook_id}/{webhook_token}")
async def execute_webhook(
    webhook_id: int,
    webhook_token: str,
    request: ExecuteWebhookRequest,
    wait: bool = False,
    thread_id: Optional[int] = None,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Execute a webhook."""
    check_rate_limit(f"execute_webhook:{webhook_id}")

    webhook = await _fetch_webhook_with_token(client, webhook_id, webhook_token)
    await webhook.send(
        content=request.content,
        username=request.username,
        avatar_url=request.avatar_url,
        tts=request.tts,
        embeds=request.embeds,
        allowed_mentions=request.allowed_mentions,
        components=request.components,
        attachments=request.attachments,
        flags=request.flags,
        wait=wait,
        thread_name=request.thread_name,
        thread_id=thread_id or request.thread_id,
    )
    return {"message": "Webhook executed"}


@router.post("/webhooks/{webhook_id}/{webhook_token}/github")
async def execute_github_webhook(
    webhook_id: int,
    webhook_token: str,
    payload: dict,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Execute a GitHub-compatible webhook."""
    check_rate_limit(f"execute_github:{webhook_id}")

    webhook = await _fetch_webhook_with_token(client, webhook_id, webhook_token)
    await webhook.send(content=payload.get("content"))
    return {"message": "GitHub webhook executed"}


@router.post("/webhooks/{webhook_id}/{webhook_token}/slack")
async def execute_slack_webhook(
    webhook_id: int,
    webhook_token: str,
    payload: dict,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Execute a Slack-compatible webhook."""
    check_rate_limit(f"execute_slack:{webhook_id}")

    webhook = await _fetch_webhook_with_token(client, webhook_id, webhook_token)
    await webhook.send(content=payload.get("content"))
    return {"message": "Slack webhook executed"}


@router.patch("/webhooks/{webhook_id}/{webhook_token}/messages/@original")
async def edit_original_webhook_message(
    webhook_id: int,
    webhook_token: str,
    request: EditWebhookMessageRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Edit the original response of a webhook."""
    check_rate_limit(f"edit_original_webhook_message:{webhook_id}")

    webhook = await _fetch_webhook_with_token(client, webhook_id, webhook_token)
    await webhook.edit_message(
        "@original",
        content=request.content,
        embeds=request.embeds,
        allowed_mentions=request.allowed_mentions,
        components=request.components,
        attachments=request.attachments,
    )
    return {"message": "Webhook message edited"}


@router.patch("/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
async def edit_webhook_message(
    webhook_id: int,
    webhook_token: str,
    message_id: str,
    request: EditWebhookMessageRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Edit a webhook message by ID."""
    check_rate_limit(f"edit_webhook_message:{webhook_id}:{message_id}")

    webhook = await _fetch_webhook_with_token(client, webhook_id, webhook_token)
    await webhook.edit_message(
        message_id,
        content=request.content,
        embeds=request.embeds,
        allowed_mentions=request.allowed_mentions,
        components=request.components,
        attachments=request.attachments,
    )
    return {"message": "Webhook message edited"}


@router.delete("/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}")
async def delete_webhook_message(
    webhook_id: int,
    webhook_token: str,
    message_id: str,
    client: commands.Bot = Depends(get_discord_client),
) -> dict:
    """Delete a webhook message."""
    check_rate_limit(f"delete_webhook_message:{webhook_id}:{message_id}")

    webhook = await _fetch_webhook_with_token(client, webhook_id, webhook_token)
    await webhook.delete_message(message_id)
    return {"message": "Webhook message deleted"}
