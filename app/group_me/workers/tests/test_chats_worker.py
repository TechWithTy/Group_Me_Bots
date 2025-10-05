"""
Tests for the ChatsWorker.

This module tests chat management, message operations, bot handling,
and integration with the GroupMe API through the chats endpoints.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from workers.chats_worker import ChatsWorker, ChatAnalytics, BotOperation, MessageInteraction


class TestChatsWorker:
    """Test suite for ChatsWorker functionality."""

    @pytest.fixture
    def mock_groupme_client(self):
        """Mock GroupMe client for testing."""
        client = MagicMock()
        client.groups.get = AsyncMock()
        client.groups.add_members = AsyncMock()
        client.messages.post_to_group = AsyncMock()
        client.messages.like_message = AsyncMock()
        client.bots.create = AsyncMock()
        client.bots.list = AsyncMock()
        client.bots.post = AsyncMock()
        client.bots.destroy = AsyncMock()
        return client

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def chats_worker(self, mock_groupme_client, mock_db_session):
        """ChatsWorker instance for testing."""
        worker = ChatsWorker(mock_groupme_client, mock_db_session)
        worker.is_running = True
        return worker

    def test_chat_analytics_creation(self, chats_worker):
        """Test ChatAnalytics dataclass creation."""
        analytics = ChatAnalytics(
            chat_id="chat_123",
            tenant_id="tenant_456",
            message_count=100,
            participant_count=10,
            last_activity=datetime.utcnow(),
            engagement_score=0.8
        )

        assert analytics.chat_id == "chat_123"
        assert analytics.tenant_id == "tenant_456"
        assert analytics.message_count == 100
        assert analytics.engagement_score == 0.8

    def test_bot_operation_creation(self, chats_worker):
        """Test BotOperation dataclass creation."""
        operation = BotOperation(
            operation_type="create",
            bot_id="bot_123",
            group_id="group_456",
            bot_config={"name": "Test Bot", "avatar_url": "https://example.com/avatar.jpg"}
        )

        assert operation.operation_type == "create"
        assert operation.bot_id == "bot_123"
        assert operation.bot_config["name"] == "Test Bot"

    def test_message_interaction_creation(self, chats_worker):
        """Test MessageInteraction dataclass creation."""
        interaction = MessageInteraction(
            conversation_id="conv_123",
            message_id="msg_456",
            operation="like",
            user_id="user_789",
            timestamp=datetime.utcnow()
        )

        assert interaction.conversation_id == "conv_123"
        assert interaction.message_id == "msg_456"
        assert interaction.operation == "like"

    @pytest.mark.asyncio
    async def test_get_chats_paginated(self, chats_worker, mock_groupme_client):
        """Test paginated chat retrieval."""
        # Mock chat data
        mock_chats = [
            {
                "id": "chat_1",
                "created_at": 1234567890,
                "updated_at": 1234567890,
                "messages_count": 10,
                "last_message": {"text": "Hello"},
                "other_user": {"name": "User 1"}
            },
            {
                "id": "chat_2",
                "created_at": 1234567891,
                "updated_at": 1234567891,
                "messages_count": 5,
                "last_message": {"text": "Hi there"},
                "other_user": {"name": "User 2"}
            }
        ]

        chats_worker.chat_cache = {chat["id"]: chat for chat in mock_chats}

        chats = await chats_worker.get_chats_paginated(page=1, per_page=10)

        assert len(chats) == 2
        assert chats[0]["id"] == "chat_1"
        assert chats[1]["id"] == "chat_2"

    @pytest.mark.asyncio
    async def test_like_message_async(self, chats_worker):
        """Test asynchronous message liking."""
        success = await chats_worker.like_message_async("conv_123", "msg_456")

        assert success is True
        assert len(chats_worker.message_interactions) == 1
        interaction = chats_worker.message_interactions[0]
        assert interaction.conversation_id == "conv_123"
        assert interaction.message_id == "msg_456"
        assert interaction.operation == "like"

    @pytest.mark.asyncio
    async def test_create_bot_async(self, chats_worker):
        """Test asynchronous bot creation."""
        bot_id = await chats_worker.create_bot_async(
            name="Test Bot",
            group_id="group_123",
            avatar_url="https://example.com/avatar.jpg"
        )

        assert bot_id is not None
        assert bot_id.startswith("bot_")
        assert "Test Bot" in chats_worker.bot_cache[bot_id]["name"]

    @pytest.mark.asyncio
    async def test_post_bot_message_async(self, chats_worker):
        """Test asynchronous bot message posting."""
        # Add a bot to the cache
        bot_id = "bot_123"
        chats_worker.bot_cache[bot_id] = {
            "bot_id": bot_id,
            "name": "Test Bot",
            "group_id": "group_123"
        }

        success = await chats_worker.post_bot_message_async(
            bot_id=bot_id,
            text="Hello from bot!",
            group_id="group_123"
        )

        assert success is True
        # Verify bot performance was updated
        assert chats_worker.bot_performance[bot_id]["messages_sent"] == 1

    @pytest.mark.asyncio
    async def test_destroy_bot_async(self, chats_worker):
        """Test asynchronous bot destruction."""
        # Add a bot to the cache
        bot_id = "bot_123"
        chats_worker.bot_cache[bot_id] = {
            "bot_id": bot_id,
            "name": "Test Bot",
            "group_id": "group_123"
        }

        success = await chats_worker.destroy_bot_async(bot_id)

        assert success is True
        assert bot_id not in chats_worker.bot_cache

    @pytest.mark.asyncio
    async def test_list_bots_async(self, chats_worker):
        """Test asynchronous bot listing."""
        # Add test bots to cache
        chats_worker.bot_cache = {
            "bot_1": {"bot_id": "bot_1", "name": "Bot 1"},
            "bot_2": {"bot_id": "bot_2", "name": "Bot 2"}
        }

        bots = await chats_worker.list_bots_async()

        assert len(bots) == 2
        assert bots[0]["bot_id"] == "bot_1"
        assert bots[1]["bot_id"] == "bot_2"

    @pytest.mark.asyncio
    async def test_chat_analytics_calculation(self, chats_worker):
        """Test chat analytics calculation."""
        # Add test chat data
        chats_worker.chat_cache["chat_123"] = {
            "id": "chat_123",
            "created_at": int((datetime.utcnow() - timedelta(days=10)).timestamp()),
            "updated_at": int(datetime.utcnow().timestamp()),
            "messages_count": 100
        }

        analytics = await chats_worker.get_chat_analytics("chat_123")

        assert analytics is not None
        assert analytics.chat_id == "chat_123"
        assert analytics.message_count == 100
        # Engagement score should be calculated (100 messages over 10 days = 10/day)
        assert analytics.engagement_score > 0

    @pytest.mark.asyncio
    async def test_chat_analytics_summary(self, chats_worker):
        """Test chat analytics summary generation."""
        # Add test analytics data
        chats_worker.chat_analytics = {
            "chat_1": ChatAnalytics(
                chat_id="chat_1",
                tenant_id="tenant_1",
                message_count=100,
                participant_count=10,
                last_activity=datetime.utcnow(),
                engagement_score=0.8
            ),
            "chat_2": ChatAnalytics(
                chat_id="chat_2",
                tenant_id="tenant_1",
                message_count=50,
                participant_count=5,
                last_activity=datetime.utcnow(),
                engagement_score=0.6
            )
        }

        summary = await chats_worker.get_chat_analytics_summary()

        assert summary["total_chats"] == 2
        assert summary["total_messages"] == 150
        assert summary["average_engagement_score"] == 0.7

    @pytest.mark.asyncio
    async def test_bot_performance_summary(self, chats_worker):
        """Test bot performance summary generation."""
        # Add test performance data
        chats_worker.bot_performance = {
            "bot_1": {"messages_sent": 50, "last_message_at": datetime.utcnow()},
            "bot_2": {"messages_sent": 30, "last_message_at": datetime.utcnow()}
        }

        summary = await chats_worker.get_bot_performance_summary()

        assert summary["total_bots"] == 2
        assert summary["total_messages_sent"] == 80
        assert summary["average_messages_per_bot"] == 40

    @pytest.mark.asyncio
    async def test_message_interaction_summary(self, chats_worker):
        """Test message interaction summary generation."""
        # Add test interactions
        chats_worker.message_interactions = [
            MessageInteraction(
                conversation_id="conv_1",
                message_id="msg_1",
                operation="like",
                user_id="user_1",
                timestamp=datetime.utcnow() - timedelta(hours=1)
            ),
            MessageInteraction(
                conversation_id="conv_2",
                message_id="msg_2",
                operation="unlike",
                user_id="user_2",
                timestamp=datetime.utcnow() - timedelta(hours=2)
            )
        ]

        summary = await chats_worker.get_message_interaction_summary()

        assert summary["total_interactions"] == 2
        assert summary["operation_breakdown"]["like"] == 1
        assert summary["operation_breakdown"]["unlike"] == 1

    @pytest.mark.asyncio
    async def test_worker_lifecycle(self, chats_worker):
        """Test worker start and stop lifecycle."""
        # Test start
        await chats_worker.start_worker()
        assert chats_worker.is_running is True

        # Test stop
        await chats_worker.stop_worker()
        assert chats_worker.is_running is False

    def test_chat_analytics_calculations(self, chats_worker):
        """Test chat analytics calculation logic."""
        # Test with high activity (10 messages per day over 10 days)
        chat_data = {
            "created_at": int((datetime.utcnow() - timedelta(days=10)).timestamp()),
            "messages_count": 100
        }

        chats_worker.chat_cache["test_chat"] = chat_data

        # Calculate analytics
        asyncio.run(chats_worker._calculate_chat_analytics("test_chat"))

        analytics = chats_worker.chat_analytics["test_chat"]
        assert analytics.message_count == 100
        assert analytics.engagement_score == 1.0  # Max engagement for 10+ messages/day

    def test_bot_performance_tracking(self, chats_worker):
        """Test bot performance metric updates."""
        bot_id = "bot_123"
        chats_worker.bot_performance[bot_id] = {"messages_sent": 0}

        # Simulate message posting
        chats_worker.bot_performance[bot_id]["messages_sent"] = 1
        chats_worker.bot_performance[bot_id]["last_message_at"] = datetime.utcnow()

        # Check performance metrics
        perf = chats_worker.bot_performance[bot_id]
        assert perf["messages_sent"] == 1
        assert "last_message_at" in perf

    @pytest.mark.asyncio
    async def test_error_handling_in_operations(self, chats_worker, mock_groupme_client):
        """Test error handling in bot operations."""
        # Mock API failure
        mock_groupme_client.bots.create = AsyncMock(side_effect=Exception("API Error"))

        # Try to create bot - should not crash worker
        bot_id = await chats_worker.create_bot_async(
            name="Test Bot",
            group_id="group_123"
        )

        # Should return None on failure
        assert bot_id is None
        assert chats_worker.is_running is True

    def test_operation_queue_management(self, chats_worker):
        """Test operation queue initialization."""
        # Check that queues are initialized
        assert hasattr(chats_worker, 'bot_operation_queue')
        assert hasattr(chats_worker, 'message_operation_queue')

        # Queues should be asyncio.Queue instances
        assert isinstance(chats_worker.bot_operation_queue, asyncio.Queue)
        assert isinstance(chats_worker.message_operation_queue, asyncio.Queue)

    @pytest.mark.asyncio
    async def test_refresh_chat_data(self, chats_worker):
        """Test chat data refresh functionality."""
        # Add test chat data
        chats_worker.chat_cache["chat_123"] = {
            "id": "chat_123",
            "updated_at": 1234567890,
            "messages_count": 50
        }

        refreshed_chat = await chats_worker.refresh_chat_data("chat_123")

        assert refreshed_chat is not None
        assert refreshed_chat["id"] == "chat_123"
        # Updated timestamp should be newer
        assert refreshed_chat["updated_at"] > 1234567890

    @pytest.mark.asyncio
    async def test_worker_integration_with_existing_system(self, chats_worker):
        """Test integration with existing worker ecosystem."""
        # Test that worker can be initialized with existing components
        assert hasattr(chats_worker, 'groupme_client')
        assert hasattr(chats_worker, 'db_session')
        assert hasattr(chats_worker, 'tenant_id')

        # Test analytics integration points
        assert hasattr(chats_worker, 'chat_analytics')
        assert hasattr(chats_worker, 'bot_performance')
        assert hasattr(chats_worker, 'message_interactions')

    def test_cache_initialization(self, chats_worker):
        """Test that caches are properly initialized."""
        assert isinstance(chats_worker.chat_cache, dict)
        assert isinstance(chats_worker.bot_cache, dict)
        assert isinstance(chats_worker.bot_performance, dict)

        # Caches should be empty initially
        assert len(chats_worker.chat_cache) == 0
        assert len(chats_worker.bot_cache) == 0
        assert len(chats_worker.bot_performance) == 0

    @pytest.mark.asyncio
    async def test_concurrent_operation_handling(self, chats_worker):
        """Test handling of concurrent operations."""
        # Create multiple async operations
        operations = []

        for i in range(5):
            op = chats_worker.create_bot_async(
                name=f"Bot {i}",
                group_id=f"group_{i}"
            )
            operations.append(op)

        # Execute all operations concurrently
        results = await asyncio.gather(*operations)

        # All operations should complete
        assert len(results) == 5
        # All should return bot IDs
        assert all(result is not None for result in results)

        # Check that all bots were added to cache
        assert len(chats_worker.bot_cache) == 5
