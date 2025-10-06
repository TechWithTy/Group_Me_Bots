"""Tests for Discord webhooks module."""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.discord.modules import webhooks


@pytest.fixture()
def fake_bot(fake_webhook):
    """Create a fake Discord bot client for webhook tests."""
    bot = MagicMock()
    bot.get_channel.return_value = MagicMock()
    bot.fetch_webhook = AsyncMock(return_value=fake_webhook)
    return bot


@pytest.fixture()
def fake_webhook():
    """Create a fake webhook object."""
    webhook = MagicMock()
    webhook.id = 444
    webhook.token = "token"
    webhook.guild_id = 555
    webhook.channel_id = 222
    webhook.name = "Test Hook"
    webhook.type = 1
    webhook.user = SimpleNamespace(id=111, name="TestUser", discriminator="0001", avatar=None, bot=False, system=False)
    webhook.edit = AsyncMock(return_value=webhook)
    webhook.delete = AsyncMock()
    webhook.send = AsyncMock()
    webhook.edit_message = AsyncMock()
    webhook.delete_message = AsyncMock()
    return webhook


@pytest.mark.asyncio
async def test_get_and_create_channel_webhooks(fake_bot, fake_webhook):
    channel = MagicMock()
    channel.webhooks = AsyncMock(return_value=[fake_webhook])
    channel.create_webhook = AsyncMock(return_value=fake_webhook)
    fake_bot.get_channel.return_value = channel

    webhooks_list = await webhooks.get_channel_webhooks(channel_id=222, client=fake_bot)
    assert webhooks_list[0].id == 444

    created = await webhooks.create_channel_webhook(
        channel_id=222,
        request=webhooks.CreateWebhookRequest(name="New Hook"),
        client=fake_bot,
    )
    assert created.id == 444
    channel.create_webhook.assert_awaited_with(name="New Hook", avatar=None, reason=None)


@pytest.mark.asyncio
async def test_update_and_delete_webhook(fake_bot, fake_webhook):
    updated = await webhooks.update_webhook(
        webhook_id=444,
        request=webhooks.UpdateWebhookRequest(name="Updated"),
        client=fake_bot,
    )
    assert updated.name == "Updated"
    fake_webhook.edit.assert_awaited_with(name="Updated", avatar=None, channel=None)

    await webhooks.delete_webhook(webhook_id=444, client=fake_bot)
    fake_webhook.delete.assert_awaited()


@pytest.mark.asyncio
async def test_execute_webhook(fake_bot, fake_webhook):
    await webhooks.execute_webhook(
        webhook_id=444,
        webhook_token="token",
        request=webhooks.ExecuteWebhookRequest(content="Hello"),
        client=fake_bot,
    )
    fake_webhook.send.assert_awaited_with(
        content="Hello",
        username=None,
        avatar_url=None,
        tts=False,
        embeds=None,
        allowed_mentions=None,
        components=None,
        attachments=None,
        flags=None,
        wait=False,
        thread_name=None,
        thread_id=None,
    )

    await webhooks.execute_github_webhook(webhook_id=444, webhook_token="token", payload={"content": "Hello"}, client=fake_bot)
    await webhooks.execute_slack_webhook(webhook_id=444, webhook_token="token", payload={"content": "Hello"}, client=fake_bot)


@pytest.mark.asyncio
async def test_edit_and_delete_webhook_message(fake_bot, fake_webhook):
    await webhooks.edit_original_webhook_message(
        webhook_id=444,
        webhook_token="token",
        request=webhooks.EditWebhookMessageRequest(content="Updated"),
        client=fake_bot,
    )
    fake_webhook.edit_message.assert_awaited_with(
        "@original",
        content="Updated",
        embeds=None,
        allowed_mentions=None,
        components=None,
        attachments=None,
    )

    await webhooks.delete_webhook_message(webhook_id=444, webhook_token="token", message_id="555", client=fake_bot)
    fake_webhook.delete_message.assert_awaited_with("555")
