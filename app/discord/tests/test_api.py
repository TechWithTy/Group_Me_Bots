"""
Tests for Discord API endpoints.

This module contains unit and integration tests for the Discord API.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import discord

# Import the app and models from the main module
from app.discord.api import app, DiscordChannel, DiscordMessage, MessageRequest, ChannelRequest

# Create test client
client = TestClient(app)

# Mock Discord client and objects
@pytest.fixture
def mock_channel():
    """Mock Discord channel."""
    channel = MagicMock()
    channel.id = 12345
    channel.name = "test-channel"
    channel.type = discord.ChannelType.text
    return channel

@pytest.fixture
def mock_message():
    """Mock Discord message."""
    message = MagicMock()
    message.id = 67890
    message.content = "Test message"
    message.author = MagicMock()
    message.author.name = "TestUser"
    message.channel = MagicMock()
    message.channel.id = 12345
    return message

@pytest.fixture
def mock_guild():
    """Mock Discord guild."""
    guild = MagicMock()
    guild.id = 11111
    guild.name = "Test Guild"
    guild.channels = []
    return guild

@pytest.fixture
def mock_bot(mock_channel, mock_guild):
    """Mock Discord bot."""
    bot = MagicMock()
    bot.is_ready.return_value = True
    bot.get_channel.return_value = mock_channel
    bot.get_guild.return_value = mock_guild
    return bot

class TestDiscordAPI:
    """Test cases for Discord API endpoints."""

    def test_root_endpoint(self):
        """Test the root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Discord API is running"}

    def test_get_channel_success(self, mock_bot):
        """Test getting a channel successfully."""
        # Patch the get_discord_client dependency
        app.dependency_overrides = {app.dependency_overrides.get: lambda: mock_bot}

        response = client.get("/channels/12345")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == 12345
        assert data["name"] == "test-channel"
        assert data["type"] == "text"

    def test_get_channel_not_found(self, mock_bot):
        """Test getting a non-existent channel."""
        mock_bot.get_channel.return_value = None

        response = client.get("/channels/99999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Channel not found"}

    def test_list_channels_success(self, mock_bot, mock_channel):
        """Test listing channels in a guild."""
        mock_bot.get_guild.return_value.channels = [mock_channel]

        response = client.get("/channels?guild_id=11111")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 12345
        assert data[0]["name"] == "test-channel"

    def test_list_channels_guild_not_found(self, mock_bot):
        """Test listing channels for non-existent guild."""
        mock_bot.get_guild.return_value = None

        response = client.get("/channels?guild_id=99999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Guild not found"}

    def test_send_message_success(self, mock_bot, mock_message):
        """Test sending a message successfully."""
        mock_bot.get_channel.return_value.send = AsyncMock(return_value=mock_message)

        request_data = {"channel_id": 12345, "content": "Hello, world!"}
        response = client.post("/messages", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == 67890
        assert data["content"] == "Test message"
        assert data["author"] == "TestUser"
        assert data["channel_id"] == 12345

    def test_send_message_channel_not_found(self, mock_bot):
        """Test sending message to non-existent channel."""
        mock_bot.get_channel.return_value = None

        request_data = {"channel_id": 99999, "content": "Hello!"}
        response = client.post("/messages", json=request_data)
        assert response.status_code == 404
        assert response.json() == {"detail": "Channel not found"}

    def test_get_messages_success(self, mock_bot, mock_channel, mock_message):
        """Test getting messages from a channel."""
        mock_channel.history = AsyncMock(return_value=[mock_message])

        response = client.get("/messages/12345")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 67890
        assert data[0]["content"] == "Test message"

    def test_get_messages_channel_not_found(self, mock_bot):
        """Test getting messages from non-existent channel."""
        mock_bot.get_channel.return_value = None

        response = client.get("/messages/99999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Channel not found"}

# Clean up dependency overrides after tests
@pytest.fixture(autouse=True)
def cleanup_overrides():
    yield
    app.dependency_overrides.clear()
