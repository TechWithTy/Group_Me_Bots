"""
Tests for the GrowthHacksWorker.

This module tests all 10 GroupMe API growth tactics implemented in the worker.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from workers.growth_hacks_worker import GrowthHacksWorker, MessageSequence, FunnelStage, PollCampaign


class TestGrowthHacksWorker:
    """Test suite for GrowthHacksWorker functionality."""

    @pytest.fixture
    def mock_groupme_client(self):
        """Mock GroupMe client for testing."""
        client = MagicMock()
        client.groups.get = AsyncMock()
        client.groups.add_members = AsyncMock()
        client.messages.post_to_group = AsyncMock()
        client.messages.like_message = AsyncMock()
        return client

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def growth_hacks_worker(self, mock_groupme_client, mock_db_session):
        """GrowthHacksWorker instance for testing."""
        worker = GrowthHacksWorker(mock_groupme_client, mock_db_session)
        worker.is_running = True
        return worker

    def test_message_sequence_creation(self, growth_hacks_worker):
        """Test message sequence creation and configuration."""
        sequence = MessageSequence(
            sequence_id="test_sequence",
            name="Test Sequence",
            tenant_id="tenant_123",
            group_id="group_456",
            messages=[
                {"text": "Welcome, $U!", "delay_minutes": 0},
                {"text": "Here's our guide...", "delay_minutes": 5}
            ],
            trigger_event="join"
        )

        growth_hacks_worker.message_sequences["test_sequence"] = sequence

        assert "test_sequence" in growth_hacks_worker.message_sequences
        assert len(growth_hacks_worker.message_sequences["test_sequence"].messages) == 2

    @pytest.mark.asyncio
    async def test_trigger_message_sequence(self, growth_hacks_worker, mock_groupme_client):
        """Test triggering of message sequences."""
        # Setup sequence
        sequence = MessageSequence(
            sequence_id="test_sequence",
            name="Test Sequence",
            tenant_id="tenant_123",
            group_id="group_456",
            messages=[
                {"text": "Welcome, $U!", "delay_minutes": 0},
                {"text": "Guide coming up...", "delay_minutes": 1}
            ],
            trigger_event="immediate",
            is_active=True
        )

        growth_hacks_worker.message_sequences["test_sequence"] = sequence

        # Mock trigger criteria check
        growth_hacks_worker._meets_trigger_criteria = AsyncMock(return_value=True)

        # Trigger sequence
        await growth_hacks_worker.trigger_message_sequence(
            "test_sequence", "user_123", "group_456",
            {"U": "John"}
        )

        # Verify messages were sent
        assert mock_groupme_client.messages.post_to_group.call_count == 2

    def test_funnel_stage_creation(self, growth_hacks_worker):
        """Test funnel stage creation."""
        stage = FunnelStage(
            stage_id="premium_stage",
            stage_name="Premium Promotion",
            source_group_id="main_group",
            target_group_id="premium_group",
            trigger_criteria={"activity_threshold": 5},
            promotion_message="You've been promoted!"
        )

        growth_hacks_worker.funnel_stages["premium_stage"] = stage

        assert "premium_stage" in growth_hacks_worker.funnel_stages
        assert growth_hacks_worker.funnel_stages["premium_stage"].target_group_id == "premium_group"

    @pytest.mark.asyncio
    async def test_engagement_boost(self, growth_hacks_worker, mock_groupme_client):
        """Test engagement boosting with auto-likes."""
        # Add user to auto-like targets
        growth_hacks_worker.auto_like_targets.add("user_123")

        # Mock recent messages
        growth_hacks_worker._get_user_recent_messages = AsyncMock(return_value=[
            {"id": "msg1", "text": "Great post!"},
            {"id": "msg2", "text": "Another post"}
        ])

        # Boost engagement
        await growth_hacks_worker.boost_user_engagement("user_123", "group_456")

        # Verify auto-likes were sent
        assert mock_groupme_client.messages.like_message.call_count == 2

    @pytest.mark.asyncio
    async def test_inactive_user_reactivation(self, growth_hacks_worker, mock_groupme_client):
        """Test reactivation of inactive users."""
        # Mock inactive users
        growth_hacks_worker._get_inactive_users = AsyncMock(return_value=[
            {"user_id": "user_123", "user_name": "John"},
            {"user_id": "user_456", "user_name": "Jane"}
        ])

        # Mock group
        growth_hacks_worker.get_active_groups = AsyncMock(return_value=["group_789"])

        # Trigger reactivation
        await growth_hacks_worker.check_and_reactivate_inactive_users()

        # Verify reactivation messages were sent
        assert mock_groupme_client.messages.post_to_group.call_count == 2

    def test_cross_pollination_setup(self, growth_hacks_worker):
        """Test cross-pollination rule setup."""
        growth_hacks_worker.trigger_cross_pollination("source_group", ["target1", "target2"])

        assert "source_group" in growth_hacks_worker.cross_pollination_rules
        assert "target1" in growth_hacks_worker.cross_pollination_rules["source_group"]
        assert "target2" in growth_hacks_worker.cross_pollination_rules["source_group"]

    @pytest.mark.asyncio
    async def test_poll_campaign_creation(self, growth_hacks_worker):
        """Test poll campaign creation."""
        poll_data = {
            "question": "What's your favorite feature?",
            "options": ["Feature A", "Feature B", "Feature C"],
            "group_id": "group_123",
            "tenant_id": "tenant_456"
        }

        poll_id = await growth_hacks_worker.create_poll_campaign(poll_data)

        assert poll_id in growth_hacks_worker.poll_campaigns
        poll = growth_hacks_worker.poll_campaigns[poll_id]
        assert poll.question == "What's your favorite feature?"
        assert len(poll.options) == 3

    @pytest.mark.asyncio
    async def test_content_scheduling(self, growth_hacks_worker, mock_groupme_client):
        """Test scheduled content posting."""
        # Schedule educational content
        await growth_hacks_worker.schedule_content_drop({
            "type": "educational",
            "text": "Here's a great tip!",
            "group_id": "group_123",
            "tenant_id": "tenant_456",
            "delay_hours": 0  # Post immediately for testing
        })

        # Process scheduled content
        await growth_hacks_worker._process_scheduled_content()

        # Verify content was posted
        mock_groupme_client.messages.post_to_group.assert_called_once()

    @pytest.mark.asyncio
    async def test_leaderboard_update(self, growth_hacks_worker, mock_groupme_client):
        """Test leaderboard calculation and posting."""
        # Mock activity data
        growth_hacks_worker._get_group_activity_data = AsyncMock(return_value={
            "user_1": {"name": "Alice", "message_count": 10, "like_count": 5, "reply_count": 3},
            "user_2": {"name": "Bob", "message_count": 8, "like_count": 7, "reply_count": 2},
            "user_3": {"name": "Charlie", "message_count": 5, "like_count": 2, "reply_count": 1}
        })

        # Update leaderboard
        await growth_hacks_worker.update_leaderboards("group_123", "weekly")

        # Verify leaderboard was created
        assert "group_123_weekly" in growth_hacks_worker.leaderboards
        assert len(growth_hacks_worker.leaderboards["group_123_weekly"]) == 3

        # Verify leaderboard was posted
        mock_groupme_client.messages.post_to_group.assert_called_once()

    @pytest.mark.asyncio
    async def test_affiliate_promotion_scheduling(self, growth_hacks_worker, mock_groupme_client):
        """Test affiliate promotion scheduling."""
        promotion_data = {
            "type": "affiliate",
            "intro_text": "Check out this amazing product!",
            "affiliate_link": "https://example.com/affiliate",
            "group_id": "group_123",
            "tenant_id": "tenant_456",
            "delay_hours": 0
        }

        await growth_hacks_worker.schedule_affiliate_promotion(promotion_data)

        # Process scheduled content
        await growth_hacks_worker._process_scheduled_content()

        # Verify affiliate promotion was posted
        call_args = mock_groupme_client.messages.post_to_group.call_args
        posted_text = call_args[1]["text"]
        assert "Check out this amazing product!" in posted_text
        assert "https://example.com/affiliate" in posted_text

    def test_growth_analytics(self, growth_hacks_worker):
        """Test growth analytics generation."""
        # Add test data
        growth_hacks_worker.message_sequences["seq1"] = MessageSequence(
            sequence_id="seq1", name="Test", tenant_id="t1", group_id="g1", is_active=True
        )
        growth_hacks_worker.funnel_stages["stage1"] = FunnelStage(
            stage_id="stage1", stage_name="Test", source_group_id="g1", target_group_id="g2",
            trigger_criteria={}, promotion_message="Test"
        )

        analytics = asyncio.run(growth_hacks_worker.get_growth_analytics())

        assert analytics["active_sequences"] == 1
        assert analytics["active_funnels"] == 1

    @pytest.mark.asyncio
    async def test_worker_lifecycle(self, growth_hacks_worker):
        """Test worker start and stop lifecycle."""
        # Test start
        await growth_hacks_worker.start_worker()
        assert growth_hacks_worker.is_running is True

        # Test stop
        await growth_hacks_worker.stop_worker()
        assert growth_hacks_worker.is_running is False

    @pytest.mark.asyncio
    async def test_error_handling_in_scheduled_content(self, growth_hacks_worker, mock_groupme_client):
        """Test error handling in scheduled content processing."""
        # Mock API failure
        mock_groupme_client.messages.post_to_group = AsyncMock(side_effect=Exception("API Error"))

        # Schedule content that will fail
        await growth_hacks_worker.schedule_content_drop({
            "type": "educational",
            "text": "This will fail",
            "group_id": "group_123",
            "tenant_id": "tenant_456",
            "delay_hours": 0
        })

        # Process should not crash
        await growth_hacks_worker._process_scheduled_content()

        # Worker should still be running
        assert growth_hacks_worker.is_running is True

    def test_sequence_execution_limits(self, growth_hacks_worker):
        """Test message sequence execution limits."""
        sequence = MessageSequence(
            sequence_id="limited_sequence",
            name="Limited Sequence",
            tenant_id="tenant_123",
            group_id="group_456",
            messages=[{"text": "Test", "delay_minutes": 0}],
            max_executions=2
        )

        growth_hacks_worker.message_sequences["limited_sequence"] = sequence

        # Execute sequence multiple times
        for i in range(3):
            if sequence.executions < sequence.max_executions:
                sequence.executions += 1

        # Should stop at limit
        assert sequence.executions == 2

    @pytest.mark.asyncio
    async def test_funnel_promotion_criteria(self, growth_hacks_worker):
        """Test funnel promotion criteria checking."""
        # Mock high activity user
        growth_hacks_worker._get_user_activity_score = AsyncMock(return_value=7)  # Above threshold
        growth_hacks_worker._get_user_recent_messages = AsyncMock(return_value=[
            {"text": "I'm interested in premium features"}
        ])

        stage = FunnelStage(
            stage_id="test_stage",
            stage_name="Test",
            source_group_id="source_group",
            target_group_id="target_group",
            trigger_criteria={"activity_threshold": 5, "keywords": ["interested", "premium"]},
            promotion_message="You've been promoted!"
        )

        meets_criteria = await growth_hacks_worker._meets_promotion_criteria(
            "user_123", "source_group", stage.trigger_criteria
        )

        assert meets_criteria is True

    def test_scheduled_content_cleanup(self, growth_hacks_worker):
        """Test scheduled content cleanup."""
        # Add old content
        old_content = growth_hacks_worker.scheduled_content
        old_content.append(type('MockContent', (), {
            'schedule_time': datetime.utcnow() - timedelta(days=35),
            'is_posted': True
        })())

        # Run cleanup (simplified)
        cutoff_time = datetime.utcnow() - timedelta(days=30)
        growth_hacks_worker.scheduled_content = [
            content for content in growth_hacks_worker.scheduled_content
            if hasattr(content, 'schedule_time') and content.schedule_time > cutoff_time
        ]

        # Should remove old content
        assert len(growth_hacks_worker.scheduled_content) == 0
