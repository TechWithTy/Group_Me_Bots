"""Tests for Discord messages module."""
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.modules import messages


@pytest.fixture()
def fake_bot(message_payload):
    """Create a fake Discord bot client."""
    bot = MagicMock()
    bot.get_channel.return_value = MagicMock()
    return bot


@pytest.fixture()
def message_payload():
    """Create a fake Discord message payload."""
    author = SimpleNamespace(
        id=111,
        name="TestUser",
        discriminator="1234",
        avatar=None,
        bot=False,
        system=False,
    )
    channel = SimpleNamespace(id=222)
    message = MagicMock()
    message.id = 333
    message.channel = channel
    message.author = author
    message.content = "Hello"
    message.created_at = datetime.utcnow()
    message.edited_at = None
    message.tts = False
    message.mention_everyone = False
    message.pinned = False
    message.type = SimpleNamespace(value=0)
    message.reactions = []
    message.add_reaction = AsyncMock()
    message.remove_reaction = AsyncMock()
    message.delete = AsyncMock()
    message.edit = AsyncMock()
    message.publish = AsyncMock()
    message.pin = AsyncMock()
    message.unpin = AsyncMock()
    return message


@pytest.mark.asyncio
async def test_get_message_success(fake_bot, message_payload):
    fake_channel = MagicMock()
    fake_channel.fetch_message = AsyncMock(return_value=message_payload)
    fake_bot.get_channel.return_value = fake_channel

    result = await messages.get_message(channel_id=222, message_id=333, client=fake_bot)
    assert result.id == 333
    assert result.channel_id == 222
    assert result.content == "Hello"


@pytest.mark.asyncio
async def test_edit_message_calls_edit(fake_bot, message_payload):
    fake_channel = MagicMock()
    fake_channel.fetch_message = AsyncMock(return_value=message_payload)
    fake_bot.get_channel.return_value = fake_channel

    await messages.edit_message(
        channel_id=222,
        message_id=333,
        request=messages.EditMessageRequest(content="Updated"),
        client=fake_bot,
    )

    message_payload.edit.assert_awaited_with(
        content="Updated",
        embeds=None,
        allowed_mentions=None,
        components=None,
        attachments=None,
        flags=None,
    )


@pytest.mark.asyncio
async def test_add_and_remove_reaction(fake_bot, message_payload):
    fake_channel = MagicMock()
    fake_channel.fetch_message = AsyncMock(return_value=message_payload)
    fake_bot.get_channel.return_value = fake_channel

    await messages.add_reaction(channel_id=222, message_id=333, emoji="👍", client=fake_bot)
    message_payload.add_reaction.assert_awaited_with("👍")

    await messages.remove_own_reaction(channel_id=222, message_id=333, emoji="👍", client=fake_bot)
    message_payload.remove_reaction.assert_awaited()


@pytest.mark.asyncio
async def test_get_reactions_returns_summary(fake_bot, message_payload):
    reaction = MagicMock()
    reaction.emoji = "👍"
    reaction.count = 2
    reaction.me = True
    reaction.users = AsyncMock(return_value=[message_payload.author])

    message_payload.reactions = [reaction]
    fake_channel = MagicMock()
    fake_channel.fetch_message = AsyncMock(return_value=message_payload)
    fake_bot.get_channel.return_value = fake_channel

    result = await messages.list_reactions(channel_id=222, message_id=333, client=fake_bot)
    assert result == [{"emoji": "👍", "count": 2, "me": True}]


@pytest.mark.asyncio
async def test_pin_and_unpin_message(fake_bot, message_payload):
    fake_channel = MagicMock()
    fake_channel.fetch_message = AsyncMock(return_value=message_payload)
    fake_channel.pins = AsyncMock(return_value=[message_payload])
    fake_bot.get_channel.return_value = fake_channel

    await messages.pin_message(channel_id=222, message_id=333, client=fake_bot)
    message_payload.pin.assert_awaited()

    pins = await messages.get_pinned_messages(channel_id=222, client=fake_bot)
    assert pins[0].id == 333

    await messages.unpin_message(channel_id=222, message_id=333, client=fake_bot)
    message_payload.unpin.assert_awaited()


@pytest.mark.asyncio
async def test_suppress_and_unsuppress_embeds(fake_bot, message_payload):
    fake_channel = MagicMock()
    fake_channel.fetch_message = AsyncMock(return_value=message_payload)
    fake_bot.get_channel.return_value = fake_channel

    await messages.suppress_embeds(channel_id=222, message_id=333, client=fake_bot)
    await messages.unsuppress_embeds(channel_id=222, message_id=333, client=fake_bot)
    assert message_payload.edit.await_count == 2


@pytest.mark.asyncio
async def test_crosspost_message(fake_bot, message_payload):
    fake_channel = MagicMock()
    fake_channel.type = SimpleNamespace(name="news")
    fake_channel.fetch_message = AsyncMock(return_value=message_payload)
    fake_bot.get_channel.return_value = fake_channel

    await messages.crosspost_message(channel_id=222, message_id=333, client=fake_bot)
    message_payload.publish.assert_awaited()
