"""Tests for Discord gateway module."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.modules import gateway


@pytest.fixture()
def fake_bot():
    """Create a fake Discord bot client for gateway tests."""
    bot = MagicMock()
    bot.http = MagicMock()
    bot.http.get_gateway = AsyncMock(return_value={"url": "wss://gateway.discord.gg"})
    bot.http.get_bot_gateway = AsyncMock(return_value={"url": "wss://gateway.discord.gg", "shards": 1, "session_start_limit": {}})
    return bot


@pytest.mark.asyncio
async def test_get_gateway_info(fake_bot):
    info = await gateway.get_gateway(client=fake_bot)
    assert info["url"] == "wss://gateway.discord.gg"
    fake_bot.http.get_gateway.assert_awaited()

    bot_info = await gateway.get_gateway_bot(client=fake_bot)
    assert bot_info["shards"] == 1
    fake_bot.http.get_bot_gateway.assert_awaited()
