"""
Tests for the EngagementWorker.

This module tests adaptive frequency control, soft opt-in mechanisms,
and engagement-based promotion strategies.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from workers.engagement_worker import EngagementWorker, EngagementProfile, AdaptiveFrequencyRule


class TestEngagementWorker:
    """Test suite for EngagementWorker functionality."""

    @pytest.fixture
    def engagement_worker(self, mock_groupme_client, mock_db_session):
        """EngagementWorker instance."""
        worker = EngagementWorker(mock_groupme_client, mock_db_session)
        worker.is_running = True
        return worker

    def test_engagement_profile_creation(self, engagement_worker):
        """Test engagement profile creation and updates."""
        profile = EngagementProfile(
            user_id="user_123",
            group_id="group_456",
            tenant_id="tenant_789"
        )

        # Test initial state
        assert profile.engagement_score == 0.0
        assert profile.activity_level == "low"
        assert profile.soft_opted_in is False

    def test_engagement_score_calculation(self, engagement_worker):
        """Test engagement score calculation."""
        profile = EngagementProfile(
            user_id="user_123",
            group_id="group_456",
            tenant_id="tenant_789",
            message_count=15,
            last_activity=datetime.utcnow()
        )

        score = engagement_worker._calculate_engagement_score(profile)
        assert 0 <= score <= 1.0

    def test_activity_level_determination(self, engagement_worker):
        """Test activity level determination."""
        assert engagement_worker._determine_activity_level(0.9) == "very_high"
        assert engagement_worker._determine_activity_level(0.7) == "high"
        assert engagement_worker._determine_activity_level(0.5) == "medium"
        assert engagement_worker._determine_activity_level(0.3) == "low"

    @pytest.mark.asyncio
    async def test_soft_opt_in_detection(self, engagement_worker):
        """Test soft opt-in signal detection."""
        profile_key = "group_456:user_123"
        profile = EngagementProfile(
            user_id="user_123",
            group_id="group_456",
            tenant_id="tenant_789",
            engagement_score=0.7
        )
        engagement_worker.engagement_profiles[profile_key] = profile

        # Test opt-in signal detection
        await engagement_worker._check_soft_opt_in_signals(
            "user_123", "I'm interested in your deals", "group_456"
        )

        assert profile.soft_opted_in is True

    def test_adaptive_frequency_calculation(self, engagement_worker):
        """Test adaptive frequency calculation."""
        rule = AdaptiveFrequencyRule(
            group_id="test_group",
            base_frequency_per_hour=2.0,
            max_frequency_per_hour=8.0
        )

        engagement_worker.frequency_rules["test_group"] = rule

        # Test base frequency
        frequency = engagement_worker.get_adaptive_frequency("test_group", "general")
        assert frequency == 2.0

        # Test with high engagement (mock)
        engagement_worker.burst_mode_active["test_group"] = True
        frequency = engagement_worker.get_adaptive_frequency("test_group", "general")
        assert frequency > 2.0  # Should increase with burst mode

    @pytest.mark.asyncio
    async def test_engagement_campaign_triggering(self, engagement_worker):
        """Test engagement campaign triggering."""
        # Mock re-engagement campaign
        with patch.object(engagement_worker, '_trigger_re_engagement_campaign') as mock_campaign:
            engagement_worker.engagement_profiles = {
                f"group_123:user_{i}": EngagementProfile(
                    user_id=f"user_{i}",
                    group_id="group_123",
                    tenant_id="tenant_789",
                    activity_level="low" if i < 7 else "high"  # 70% low engagement
                ) for i in range(10)
            }

            await engagement_worker._check_campaign_triggers()

            # Should trigger re-engagement for groups with high low-engagement rate
            mock_campaign.assert_called_once()

    @pytest.mark.asyncio
    async def test_engagement_analytics(self, engagement_worker):
        """Test engagement analytics generation."""
        # Add test profiles
        engagement_worker.engagement_profiles = {
            "group1:user1": EngagementProfile(user_id="user1", group_id="group1", tenant_id="tenant1", engagement_score=0.8),
            "group1:user2": EngagementProfile(user_id="user2", group_id="group1", tenant_id="tenant1", engagement_score=0.6),
            "group1:user3": EngagementProfile(user_id="user3", group_id="group1", tenant_id="tenant1", engagement_score=0.3, soft_opted_in=True)
        }

        analytics = await engagement_worker.get_engagement_analytics()

        assert analytics["total_users_tracked"] == 3
        assert analytics["active_users"] == 2  # Users with high/very_high engagement
        assert analytics["soft_opted_in_users"] == 1
