"""Tests for Discord voice module."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.modules import voice


@pytest.fixture()
def fake_bot():
    """Create a fake Discord bot client for voice tests."""
    return MagicMock()


@pytest.mark.asyncio
async def test_get_voice_regions(fake_bot):
    fake_bot.http = MagicMock()
    fake_bot.http.get_voice_regions = AsyncMock(return_value=[
        {"id": "us-east", "name": "US East", "optimal": True, "deprecated": False, "custom": False}
    ])

    regions = await voice.get_voice_regions(client=fake_bot)
    assert regions[0].id == "us-east"


@pytest.mark.asyncio
async def test_get_and_update_voice_state(fake_bot):
    fake_member = MagicMock()
    fake_member.id = 111
    fake_member.voice = SimpleNamespace(
        channel=SimpleNamespace(id=222),
        user_id=111,
        session_id="sess",
        deaf=False,
        mute=False,
        self_deaf=False,
        self_mute=True,
        self_stream=False,
        self_video=False,
        suppress=False,
        request_to_speak_timestamp=None,
    )

    fake_guild = MagicMock()
    fake_guild.get_member.return_value = fake_member
    fake_guild.fetch_member = AsyncMock(return_value=fake_member)
    fake_guild.change_voice_state = AsyncMock()
    fake_bot.get_guild.return_value = fake_guild

    state = await voice.get_voice_state(guild_id=999, user_id=111, client=fake_bot)
    assert state.user_id == 111

    await voice.update_my_voice_state(
        guild_id=999,
        request=voice.UpdateVoiceStateRequest(channel_id=222, self_mute=False, self_deaf=False),
        client=fake_bot,
    )
    fake_guild.change_voice_state.assert_awaited()
