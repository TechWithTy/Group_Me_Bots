"""
Tests for the ContentEchoWorker.

This module tests content echoing, cross-group sharing, and engagement-based content promotion.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from workers.content_echo_worker import ContentEchoWorker, EchoRule, ContentEcho


class TestContentEchoWorker:
    """Test suite for ContentEchoWorker functionality."""

    @pytest.fixture
    def mock_groupme_client(self):
        """Mock GroupMe client."""
        client = MagicMock()
        client.groups.get = AsyncMock()
        client.messages.post_to_group = AsyncMock()
        return client

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def content_echo_worker(self, mock_groupme_client, mock_db_session):
        """ContentEchoWorker instance."""
        worker = ContentEchoWorker(mock_groupme_client, mock_db_session)
        worker.is_running = True
        return worker

    def test_echo_rule_creation(self, content_echo_worker):
        """Test echo rule creation and management."""
        rule = EchoRule(
            source_group_id="source_group",
            target_group_ids=["target1", "target2"],
            content_filters=["deal", "offer"],
            engagement_threshold=5
        )

        content_echo_worker.add_echo_rule(rule)

        assert "source_group" in content_echo_worker.echo_rules
        assert content_echo_worker.echo_rules["source_group"].engagement_threshold == 5

    @pytest.mark.asyncio
    async def test_should_echo_content(self, content_echo_worker):
        """Test content filtering for echoing."""
        rule = EchoRule(
            source_group_id="test_group",
            target_group_ids=["target"],
            content_filters=["deal", "discount"],
            echo_probability=1.0  # Always echo for testing
        )

        content_echo_worker.echo_rules["test_group"] = rule

        # Should echo content with matching keywords
        should_echo = await content_echo_worker._should_echo_content("Great deal on shoes!", rule)
        assert should_echo is True

        # Should not echo content without matching keywords
        should_echo = await content_echo_worker._should_echo_content("Just saying hello", rule)
        assert should_echo is False

    @pytest.mark.asyncio
    async def test_echo_content_to_targets(self, content_echo_worker, mock_groupme_client):
        """Test echoing content to target groups."""
        # Setup mock response
        mock_response = {"message": {"id": "echoed_message_123"}}
        mock_groupme_client.messages.post_to_group = AsyncMock(return_value=mock_response)

        message_data = {
            "id": "original_123",
            "group_id": "source_group",
            "text": "Amazing deal alert!",
            "name": "User123"
        }

        rule = EchoRule(
            source_group_id="source_group",
            target_group_ids=["target_group"],
            attribution_required=True
        )

        content_echo_worker.echo_rules["source_group"] = rule

        await content_echo_worker._echo_content_to_targets(message_data, rule, 10)

        # Verify message was posted to target group
        mock_groupme_client.messages.post_to_group.assert_called_once()

        # Verify echo was recorded
        assert len(content_echo_worker.echo_history) == 1
        echo = content_echo_worker.echo_history[0]
        assert echo.source_group_id == "source_group"
        assert echo.target_group_id == "target_group"

    @pytest.mark.asyncio
    async def test_echo_analytics(self, content_echo_worker):
        """Test echo analytics generation."""
        # Add some test echo data
        echo1 = ContentEcho(
            source_group_id="source1",
            target_group_id="target1",
            original_message_id="msg1",
            original_message_text="Test message 1",
            echoed_message_id="echo1",
            echo_timestamp=datetime.utcnow(),
            engagement_score=5
        )

        echo2 = ContentEcho(
            source_group_id="source1",
            target_group_id="target2",
            original_message_id="msg2",
            original_message_text="Test message 2",
            echoed_message_id="echo2",
            echo_timestamp=datetime.utcnow(),
            engagement_score=8
        )

        content_echo_worker.echo_history = [echo1, echo2]

        analytics = await content_echo_worker.get_echo_analytics()

        assert analytics["total_echoes"] == 2
        assert analytics["average_engagement_score"] == 6.5
        assert "source1" in analytics["echoes_by_source"]

    def test_hourly_echo_limits(self, content_echo_worker):
        """Test hourly echo rate limiting."""
        rule = EchoRule(
            source_group_id="test_group",
            target_group_ids=["target"],
            max_echoes_per_hour=3
        )

        content_echo_worker.echo_rules["test_group"] = rule

        # Simulate reaching hourly limit
        current_hour = datetime.utcnow().hour
        content_echo_worker.hourly_echo_counts[f"test_group_{current_hour}"] = 3

        # Should not echo when at limit
        should_echo = asyncio.run(content_echo_worker._should_echo_content("Test message", rule))
        assert should_echo is False

    @pytest.mark.asyncio
    async def test_content_mining_analysis(self, content_echo_worker):
        """Test content mining and analysis."""
        # Mock content analysis methods
        content_echo_worker._analyze_content_patterns = AsyncMock(return_value={"test": "patterns"})
        content_echo_worker._identify_trending_topics = AsyncMock(return_value=["test", "trending"])
        content_echo_worker._find_high_engagement_content = AsyncMock(return_value=[{"test": "content"}])

        mining_results = await content_echo_worker.run_content_mining()

        assert "content_patterns" in mining_results
        assert "trending_topics" in mining_results
        assert "high_engagement_content" in mining_results

    def test_echo_rule_removal(self, content_echo_worker):
        """Test echo rule removal."""
        rule = EchoRule(source_group_id="test_group", target_group_ids=["target"])
        content_echo_worker.add_echo_rule(rule)

        assert "test_group" in content_echo_worker.echo_rules

        content_echo_worker.remove_echo_rule("test_group")

        assert "test_group" not in content_echo_worker.echo_rules

    @pytest.mark.asyncio
    async def test_echo_loop_prevention(self, content_echo_worker):
        """Test prevention of echo loops."""
        # Test that source and target groups are different
        can_echo = await content_echo_worker._can_echo_to_group("source", "source")
        assert can_echo is False  # Should not echo to same group

        # Test recent echo prevention
        content_echo_worker.echo_history = [
            ContentEcho(
                source_group_id="source",
                target_group_id="target",
                original_message_id="msg1",
                original_message_text="test",
                echoed_message_id="echo1",
                echo_timestamp=datetime.utcnow()
            )
        ] * 3  # 3 recent echoes

        can_echo = await content_echo_worker._can_echo_to_group("source", "target")
        assert can_echo is False  # Should not echo due to recent activity
