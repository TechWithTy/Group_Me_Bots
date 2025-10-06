"""Tests for Discord interactions module."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.modules import interactions


@pytest.fixture()
def fake_bot():
    """Create a fake Discord bot client for interaction tests."""
    bot = MagicMock()
    bot.http = MagicMock()
    bot.http.get_guild_command_permissions = AsyncMock(return_value={"id": "cmd", "permissions": []})
    bot.http.put_guild_command_permissions = AsyncMock(return_value={"id": "cmd", "permissions": []})
    return bot


@pytest.mark.asyncio
async def test_create_interaction_response(fake_bot):
    payload = interactions.InteractionCallback(data={"content": "Hello"}, type=4)
    response = await interactions.create_interaction_response(payload)
    assert response.data["content"] == "Hello"


@pytest.mark.asyncio
async def test_get_and_set_command_permissions(fake_bot):
    permissions = await interactions.get_command_permissions(
        application_id=1,
        guild_id=2,
        command_id=3,
        client=fake_bot,
    )
    assert permissions["id"] == "cmd"
    fake_bot.http.get_guild_command_permissions.assert_awaited_with(1, 2, 3)

    payload = interactions.CommandPermissionsUpdate(permissions=[{"id": "role", "type": 1, "permission": True}])
    result = await interactions.set_command_permissions(
        application_id=1,
        guild_id=2,
        command_id=3,
        request=payload,
        client=fake_bot,
    )
    assert result["id"] == "cmd"
    fake_bot.http.put_guild_command_permissions.assert_awaited_with(1, 2, 3, payload.permissions)
