"""
Tests for the ConversionWorker.

This module tests conversion tracking, funnel analysis, and optimization strategies.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from workers.conversion_worker import ConversionWorker, ConversionFunnel, UserJourney


class TestConversionWorker:
    """Test suite for ConversionWorker functionality."""

    @pytest.fixture
    def conversion_worker(self, mock_groupme_client, mock_db_session):
        """ConversionWorker instance."""
        worker = ConversionWorker(mock_groupme_client, mock_db_session)
        worker.is_running = True
        return worker

    def test_conversion_funnel_creation(self, conversion_worker):
        """Test conversion funnel setup."""
        funnel = ConversionFunnel(
            funnel_id="test_funnel",
            funnel_name="Test Conversion Funnel",
            tenant_id="tenant_123",
            stages=["awareness", "interest", "purchase"],
            conversion_goals={"purchase": "completed_checkout"}
        )

        conversion_worker.active_funnels["test_funnel"] = funnel

        assert "test_funnel" in conversion_worker.active_funnels
        assert len(conversion_worker.active_funnels["test_funnel"].stages) == 3

    @pytest.mark.asyncio
    async def test_user_journey_tracking(self, conversion_worker):
        """Test user journey creation and updates."""
        # Start a user journey
        await conversion_worker._start_user_journey("user_123", "group_456", "tenant_789")

        assert len(conversion_worker.user_journeys) == 1

        journey = list(conversion_worker.user_journeys.values())[0]
        assert journey.user_id == "user_123"
        assert journey.current_stage == "awareness"

    @pytest.mark.asyncio
    async def test_conversion_event_tracking(self, conversion_worker):
        """Test conversion event processing."""
        # Track a purchase event
        event_data = {
            "event_type": "purchase_completed",
            "user_id": "user_123",
            "group_id": "group_456",
            "value": 29.99,
            "category": "premium_plan"
        }

        await conversion_worker.track_conversion_event(event_data)

        # Verify event was recorded
        assert len(conversion_worker.conversion_events) == 1
        assert conversion_worker.conversion_events[0]["event_type"] == "purchase_completed"

    @pytest.mark.asyncio
    async def test_journey_stage_progression(self, conversion_worker):
        """Test user journey stage progression."""
        # Start journey
        await conversion_worker._start_user_journey("user_123", "group_456", "tenant_789")

        journey_id = list(conversion_worker.user_journeys.keys())[0]
        journey = conversion_worker.user_journeys[journey_id]

        # Simulate interest event
        await conversion_worker._update_user_journey("user_123", "tenant_789", {"event_type": "bot_response"})

        assert journey.current_stage == "interest"
        assert len(journey.stages_visited) == 2  # awareness -> interest

    @pytest.mark.asyncio
    async def test_conversion_funnel_analysis(self, conversion_worker):
        """Test conversion funnel analysis."""
        # Setup test data
        conversion_worker.active_funnels["test_funnel"] = ConversionFunnel(
            funnel_id="test_funnel",
            funnel_name="Test Funnel",
            tenant_id="tenant_123",
            stages=["awareness", "interest", "purchase"],
            conversion_goals={"purchase": "completed"}
        )

        # Add test journeys
        journey1 = UserJourney(user_id="user1", tenant_id="tenant_123", group_id="group1")
        journey1.conversion_completed = True
        journey1.conversion_timestamp = datetime.utcnow()

        journey2 = UserJourney(user_id="user2", tenant_id="tenant_123", group_id="group1")
        journey2.conversion_completed = False

        conversion_worker.user_journeys = {
            "journey1": journey1,
            "journey2": journey2
        }

        analytics = await conversion_worker.get_conversion_analytics()

        assert analytics["journey_completion_rate"] == 0.5  # 1 out of 2 completed

    def test_ab_test_setup(self, conversion_worker):
        """Test A/B test configuration."""
        test_config = {
            "name": "Premium Pitch Test",
            "type": "monetization_strategy",
            "variants": [
                {"name": "discount", "template": "Get 20% off!"},
                {"name": "features", "template": "Premium features included!"}
            ],
            "target_metric": "conversion_rate"
        }

        test_id = conversion_worker.setup_ab_test(test_config)

        assert test_id in conversion_worker.ab_tests
        assert conversion_worker.ab_tests[test_id]["test_name"] == "Premium Pitch Test"

    @pytest.mark.asyncio
    async def test_ab_test_analysis(self, conversion_worker):
        """Test A/B test result analysis."""
        # Setup test
        test_config = {
            "name": "Test",
            "variants": [{"name": "A"}, {"name": "B"}],
            "start_date": datetime.utcnow() - timedelta(hours=1)
        }

        test_id = conversion_worker.setup_ab_test(test_config)

        # Add test conversion events
        for i in range(10):
            event = {
                "event_type": "purchase_completed",
                "user_id": f"user_{i}",
                "timestamp": datetime.utcnow()
            }
            conversion_worker.conversion_events.append(event)

        results = await conversion_worker.run_ab_test_analysis(test_id)

        assert "variant_results" in results
        assert results["total_conversions"] == 10
