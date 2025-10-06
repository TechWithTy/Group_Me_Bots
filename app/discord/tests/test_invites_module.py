"""Tests for Discord invites module."""
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.modules import invites
from app.discord.modules.models import CreateChannelInviteRequest


@pytest.fixture()
def fake_bot(fake_invite):
    """Create a fake Discord bot client for invite tests."""
    bot = MagicMock()
    bot.get_channel.return_value = MagicMock()
    bot.get_guild.return_value = MagicMock()
    bot.fetch_invite = AsyncMock(return_value=fake_invite)
    bot.delete_invite = AsyncMock()
    return bot


@pytest.fixture()
def fake_invite():
    """Create a fake invite object."""
    invite = MagicMock()
    invite.code = "abc123"
    invite.guild = SimpleNamespace(id=999, name="Guild")
    invite.channel = SimpleNamespace(id=222, name="channel", type=SimpleNamespace(name="text"))
    invite.inviter = SimpleNamespace(id=111, name="TestUser", discriminator="0001", avatar=None, bot=False, system=False)
    invite.uses = 0
    invite.max_uses = 0
    invite.max_age = 0
    invite.temporary = False
    invite.created_at = datetime.utcnow()
    invite.target_type = None
    invite.target_user = None
    invite.target_application = None
    invite.approximate_member_count = None
    invite.approximate_presence_count = None
    invite.expires_at = None
    invite.stage_instance = None
    invite.guild_scheduled_event = None
    invite.delete = AsyncMock()
    return invite


@pytest.mark.asyncio
async def test_channel_invites(fake_bot, fake_invite):
    channel = MagicMock()
    channel.invites = AsyncMock(return_value=[fake_invite])
    channel.create_invite = AsyncMock(return_value=fake_invite)
    fake_bot.get_channel.return_value = channel

    invites_list = await invites.get_channel_invites(channel_id=222, client=fake_bot)
    assert invites_list[0].code == "abc123"

    created = await invites.create_channel_invite(
        channel_id=222,
        request=CreateChannelInviteRequest(),
        client=fake_bot,
    )
    assert created.code == "abc123"
    channel.create_invite.assert_awaited()


@pytest.mark.asyncio
async def test_guild_and_global_invites(fake_bot, fake_invite):
    guild = MagicMock()
    guild.invites = AsyncMock(return_value=[fake_invite])
    fake_bot.get_guild.return_value = guild

    guild_invites = await invites.get_guild_invites(guild_id=999, client=fake_bot)
    assert guild_invites[0].code == "abc123"

    invite_info = await invites.get_invite(invite_code="abc123", client=fake_bot)
    assert invite_info.code == "abc123"

    await invites.delete_invite(invite_code="abc123", client=fake_bot)
    fake_bot.delete_invite.assert_awaited_with("abc123")
