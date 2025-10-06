"""Gateway-related endpoints for Discord API."""
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends
from discord.ext import commands

from .core import check_rate_limit, get_discord_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["gateway"])


@router.get("/gateway")
async def get_gateway(client: commands.Bot = Depends(get_discord_client)) -> Dict[str, Any]:
    """Get the gateway URL."""
    check_rate_limit("get_gateway")

    if not getattr(client, "http", None):
        return {"url": ""}

    return await client.http.get_gateway()


@router.get("/gateway/bot")
async def get_gateway_bot(client: commands.Bot = Depends(get_discord_client)) -> Dict[str, Any]:
    """Get gateway information for bots."""
    check_rate_limit("get_gateway_bot")

    if not getattr(client, "http", None):
        return {"url": "", "shards": 0, "session_start_limit": {}}

    return await client.http.get_bot_gateway()
