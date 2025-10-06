"""Tests for Discord OAuth2 module."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.modules import oauth2
from app.discord.modules.oauth2 import OAuth2TokenRequest, OAuth2TokenRevokeRequest


@pytest.fixture()
def fake_bot():
    """Create a fake Discord bot client for OAuth2 tests."""
    bot = MagicMock()
    bot.http = MagicMock()
    bot.http.request = AsyncMock(side_effect=[
        {"access_token": "token", "token_type": "Bearer"},
        {"revoked": True},
        {"application": {"id": "app"}},
    ])
    return bot


@pytest.mark.asyncio
async def test_token_management(fake_bot):
    exchange = await oauth2.exchange_token(
        request=OAuth2TokenRequest(grant_type="client_credentials", client_id="id", client_secret="secret"),
        client=fake_bot,
    )
    assert exchange["access_token"] == "token"

    revoke = await oauth2.revoke_token(
        request=OAuth2TokenRevokeRequest(token="token", token_type_hint="access_token"),
        client=fake_bot,
    )
    assert revoke["revoked"] is True

    me = await oauth2.get_current_authorization(client=fake_bot)
    assert me["application"]["id"] == "app"
