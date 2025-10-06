"""OAuth2-related endpoints for Discord API."""
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from discord.ext import commands

from .core import check_rate_limit, get_discord_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["oauth2"])


class OAuth2TokenRequest(BaseModel):
    """Request model for exchanging OAuth2 tokens."""
    grant_type: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class OAuth2TokenRevokeRequest(BaseModel):
    """Request model for revoking OAuth2 tokens."""
    token: str
    token_type_hint: Optional[str] = None


async def _make_request(client: commands.Bot, method: str, path: str, data: Dict[str, Any]):
    if not getattr(client, "http", None):
        return {}
    return await client.http.request(method, path, data=data)


@router.post("/oauth2/token")
async def exchange_token(
    request: OAuth2TokenRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> Dict[str, Any]:
    """Exchange an OAuth2 token."""
    check_rate_limit("exchange_token")

    data = request.dict(exclude_none=True)
    return await _make_request(client, "POST", "/oauth2/token", data)


@router.post("/oauth2/token/revoke")
async def revoke_token(
    request: OAuth2TokenRevokeRequest,
    client: commands.Bot = Depends(get_discord_client),
) -> Dict[str, Any]:
    """Revoke an OAuth2 token."""
    check_rate_limit("revoke_token")

    data = request.dict(exclude_none=True)
    return await _make_request(client, "POST", "/oauth2/token/revoke", data)


@router.post("/oauth2/@me")
async def get_current_authorization(client: commands.Bot = Depends(get_discord_client)) -> Dict[str, Any]:
    """Get current OAuth2 authorization info."""
    check_rate_limit("get_oauth2_me")

    return await _make_request(client, "GET", "/oauth2/@me", {})
