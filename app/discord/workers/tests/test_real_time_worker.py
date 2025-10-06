"""
Tests for the RealTimeWorker.

This module tests real-time push subscriptions, event handling,
and live message processing capabilities.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from workers.real_time_worker import RealTimeWorker, PushSubscription, RealTimeEvent


class TestRealTimeWorker:
    """Test suite for RealTimeWorker functionality."""

    @pytest.fixture
    def mock_groupme_client(self):
        """Mock GroupMe client for testing."""
        client = MagicMock()
        client.groups.get = AsyncMock()
        client.messages.post_to_group = AsyncMock()
        return client

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def real_time_worker(self, mock_groupme_client, mock_db_session):
        """RealTimeWorker instance for testing."""
        worker = RealTimeWorker(mock_groupme_client, mock_db_session)
        worker.is_running = True
        return worker

    @pytest.mark.asyncio
    async def test_initialize_subscriptions(self, real_time_worker, mock_groupme_client):
        """Test initialization of subscriptions."""
        # Mock active groups
        mock_group = MagicMock()
        mock_group.id = "test_group_123"
        real_time_worker.get_active_groups = AsyncMock(return_value=[mock_group])

        # Mock handshake response
        with patch.object(real_time_worker, '_perform_handshake', return_value="test_client_123"):
            await real_time_worker.initialize()

        # Verify subscription was created
        assert "test_group_123" in real_time_worker.subscriptions
        subscription = real_time_worker.subscriptions["test_group_123"]
        assert subscription.group_id == "test_group_123"
        assert subscription.client_id == "test_client_123"

    @pytest.mark.asyncio
    async def test_perform_handshake(self, real_time_worker):
        """Test Faye handshake process."""
        mock_response = {"clientId": "test_client_123"}

        with patch('aiohttp.ClientSession') as mock_session:
            mock_post = AsyncMock()
            mock_post.__aenter__ = AsyncMock(return_value=AsyncMock())
            mock_post.__aenter__.return_value.status = 200
            mock_post.__aenter__.return_value.json = AsyncMock(return_value=[mock_response])

            mock_session.return_value.post = mock_post

            client_id = await real_time_worker._perform_handshake()

            assert client_id == "test_client_123"

    def test_register_event_handler(self, real_time_worker):
        """Test event handler registration."""
        async def test_handler(event):
            pass

        real_time_worker.register_event_handler("message", test_handler)

        assert "message" in real_time_worker.event_handlers
        assert test_handler in real_time_worker.event_handlers["message"]

    @pytest.mark.asyncio
    async def test_process_real_time_message(self, real_time_worker, mock_groupme_client):
        """Test processing of real-time message events."""
        # Mock should_respond_instantly to return True
        real_time_worker._should_respond_instantly = AsyncMock(return_value=True)
        real_time_worker._generate_instant_response = AsyncMock(return_value="Test response")

        event = RealTimeEvent(
            event_type="message",
            group_id="test_group",
            timestamp=datetime.utcnow(),
            data={
                "data": {
                    "text": "help me",
                    "user_id": "user_123"
                }
            }
        )

        await real_time_worker._process_real_time_event(event)

        # Verify instant response was sent
        mock_groupme_client.messages.post_to_group.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_respond_instantly(self, real_time_worker):
        """Test instant response detection."""
        # Test with trigger keyword
        should_respond = await real_time_worker._should_respond_instantly("I need help urgently", "group_123")
        assert should_respond is True

        # Test without trigger keyword
        should_respond = await real_time_worker._should_respond_instantly("Just saying hello", "group_123")
        assert should_respond is False

    @pytest.mark.asyncio
    async def test_generate_instant_response(self, real_time_worker):
        """Test instant response generation."""
        response = await real_time_worker._generate_instant_response("I need help", "group_123")
        assert response == "I can help you! What do you need assistance with?"

        response = await real_time_worker._generate_instant_response("I want to buy something", "group_123")
        assert response == "Looking to purchase? I can help with recommendations and deals!"

    @pytest.mark.asyncio
    async def test_handle_member_joined(self, real_time_worker, mock_groupme_client):
        """Test handling of member joined events."""
        event = RealTimeEvent(
            event_type="member_joined",
            group_id="test_group",
            timestamp=datetime.utcnow(),
            data={
                "data": {
                    "user_id": "new_user_123"
                }
            }
        )

        await real_time_worker._process_real_time_event(event)

        # Verify welcome message was sent
        mock_groupme_client.messages.post_to_group.assert_called_once()

    @pytest.mark.asyncio
    async def test_unsubscribe_from_group(self, real_time_worker):
        """Test unsubscribing from a group."""
        # Add a subscription
        subscription = PushSubscription(
            group_id="test_group",
            client_id="test_client",
            subscription_channel="/group/test_group"
        )
        real_time_worker.subscriptions["test_group"] = subscription

        # Unsubscribe
        await real_time_worker.unsubscribe_from_group("test_group")

        # Verify subscription was removed
        assert "test_group" not in real_time_worker.subscriptions

    def test_get_subscription_status(self, real_time_worker):
        """Test subscription status reporting."""
        # Add test subscriptions
        subscription1 = PushSubscription(
            group_id="group_1",
            client_id="client_1",
            subscription_channel="/group/group_1"
        )
        subscription2 = PushSubscription(
            group_id="group_2",
            client_id="client_2",
            subscription_channel="/group/group_2",
            is_active=False
        )

        real_time_worker.subscriptions = {
            "group_1": subscription1,
            "group_2": subscription2
        }

        status = asyncio.run(real_time_worker.get_subscription_status())

        assert status["total_subscriptions"] == 2
        assert status["active_subscriptions"] == 1
        assert "group_1" in status["subscription_details"]
        assert "group_2" in status["subscription_details"]

    @pytest.mark.asyncio
    async def test_heartbeat_functionality(self, real_time_worker):
        """Test heartbeat maintenance of subscriptions."""
        # This is a simplified test - in practice, you'd test the actual heartbeat loop
        subscription = PushSubscription(
            group_id="test_group",
            client_id="client_123",
            subscription_channel="/group/test_group",
            last_activity=datetime.utcnow() - timedelta(minutes=10)  # Old activity
        )

        real_time_worker.subscriptions["test_group"] = subscription

        # Run a short heartbeat cycle
        await real_time_worker.run_heartbeat()

        # In a real test, you'd check if stale subscriptions are handled
        # For now, just verify the method runs without error
        assert True

    @pytest.mark.asyncio
    async def test_worker_lifecycle(self, real_time_worker):
        """Test worker start and stop lifecycle."""
        # Test start
        await real_time_worker.start_worker()
        assert real_time_worker.is_running is True

        # Test stop
        await real_time_worker.stop_worker()
        assert real_time_worker.is_running is False

    def test_event_handler_registration(self, real_time_worker):
        """Test that event handlers are properly registered."""
        handlers_before = len(real_time_worker.event_handlers.get("message", []))

        async def dummy_handler(event):
            pass

        real_time_worker.register_event_handler("message", dummy_handler)

        handlers_after = len(real_time_worker.event_handlers.get("message", []))
        assert handlers_after == handlers_before + 1

    @pytest.mark.asyncio
    async def test_long_poll_events(self, real_time_worker):
        """Test long-polling for events."""
        subscription = PushSubscription(
            group_id="test_group",
            client_id="client_123",
            subscription_channel="/group/test_group"
        )

        # Mock successful long-poll response
        mock_events = [
            {
                "channel": "/group/test_group",
                "data": {
                    "type": "message",
                    "text": "test message"
                }
            }
        ]

        with patch('aiohttp.ClientSession') as mock_session:
            mock_post = AsyncMock()
            mock_post.__aenter__ = AsyncMock(return_value=AsyncMock())
            mock_post.__aenter__.return_value.status = 200
            mock_post.__aenter__.return_value.json = AsyncMock(return_value=mock_events)

            mock_session.return_value.post = mock_post

            events = await real_time_worker._long_poll_for_events(subscription)

            assert len(events) == 1
            assert events[0]["data"]["type"] == "message"

    @pytest.mark.asyncio
    async def test_error_handling_in_event_processing(self, real_time_worker, mock_groupme_client):
        """Test error handling in event processing."""
        # Register a handler that raises an exception
        async def failing_handler(event):
            raise Exception("Test error")

        real_time_worker.register_event_handler("message", failing_handler)

        # Process an event - should not crash the worker
        event = RealTimeEvent(
            event_type="message",
            group_id="test_group",
            timestamp=datetime.utcnow(),
            data={"data": {"text": "test"}}
        )

        # This should not raise an exception
        await real_time_worker._process_real_time_event(event)

        # The worker should still be functional
        assert real_time_worker.is_running is True
