"""
Tests for the SegmentationWorker.

This module tests automatic user segmentation, micro-group creation,
and targeted messaging strategies.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from workers.segmentation_worker import SegmentationWorker, UserSegment, MicroGroup


class TestSegmentationWorker:
    """Test suite for SegmentationWorker functionality."""

    @pytest.fixture
    def segmentation_worker(self, mock_groupme_client, mock_db_session):
        """SegmentationWorker instance."""
        worker = SegmentationWorker(mock_groupme_client, mock_db_session)
        worker.is_running = True
        return worker

    def test_user_segment_creation(self, segmentation_worker):
        """Test user segment creation and management."""
        segment = UserSegment(
            segment_id="tech_enthusiasts",
            segment_name="Tech Enthusiasts",
            tenant_id="tenant_123",
            keywords=["programming", "AI", "software"],
            engagement_threshold=0.7
        )

        segmentation_worker.add_user_segment(segment)

        assert "tech_enthusiasts" in segmentation_worker.user_segments
        assert segmentation_worker.user_segments["tech_enthusiasts"].keywords == ["programming", "AI", "software"]

    @pytest.mark.asyncio
    async def test_user_segmentation_analysis(self, segmentation_worker):
        """Test user message analysis for segmentation."""
        # Add test segment
        segment = UserSegment(
            segment_id="deal_seekers",
            segment_name="Deal Seekers",
            tenant_id="tenant_123",
            keywords=["deal", "discount", "offer"],
            engagement_threshold=0.5
        )
        segmentation_worker.add_user_segment(segment)

        # Mock user activity
        segmentation_worker._get_user_activity = AsyncMock(return_value={
            "message_count": 5,
            "engagement_score": 0.7,
            "activity_pattern": "regular"
        })

        matching_segments = await segmentation_worker.analyze_user_for_segmentation(
            "user_123", "group_456", "Looking for great deals on tech!"
        )

        assert "deal_seekers" in matching_segments

    @pytest.mark.asyncio
    async def test_micro_group_creation(self, segmentation_worker, mock_groupme_client):
        """Test micro-group creation."""
        # Mock GroupMe API response
        mock_response = {
            "id": "micro_group_123",
            "share_url": "https://groupme.com/join/abc123"
        }
        mock_groupme_client.groups.create_group = AsyncMock(return_value=mock_response)

        micro_group_id = await segmentation_worker.create_micro_group(
            "parent_group_456", "deal_seekers"
        )

        assert micro_group_id == "micro_group_123"
        assert "micro_group_123" in segmentation_worker.micro_groups

    @pytest.mark.asyncio
    async def test_user_invitation_to_micro_group(self, segmentation_worker, mock_groupme_client):
        """Test user invitation to micro-groups."""
        # Setup micro-group
        micro_group = MicroGroup(
            group_id="micro_123",
            parent_group_id="parent_456",
            segment_id="deal_seekers",
            tenant_id="tenant_789",
            group_name="Deal Seekers Group"
        )
        segmentation_worker.micro_groups["micro_123"] = micro_group

        # Mock successful invitation
        mock_groupme_client.groups.add_members = AsyncMock()

        success = await segmentation_worker.invite_user_to_micro_group("user_123", "micro_123")

        assert success is True
        assert micro_group.member_count == 1

    @pytest.mark.asyncio
    async def test_automatic_segmentation_run(self, segmentation_worker):
        """Test automatic segmentation analysis."""
        # Mock group messages
        segmentation_worker._get_recent_group_messages = AsyncMock(return_value=[
            {"user_id": "user_1", "text": "Looking for deals!"},
            {"user_id": "user_2", "text": "Tech discussion here"}
        ])

        # Mock segmentation analysis
        segmentation_worker.analyze_user_for_segmentation = AsyncMock(return_value=["deal_seekers"])
        segmentation_worker._get_or_create_micro_group = AsyncMock(return_value="micro_123")
        segmentation_worker.invite_user_to_micro_group = AsyncMock(return_value=True)

        results = await segmentation_worker.run_automatic_segmentation()

        assert results["total_users_analyzed"] == 2
        assert results["users_segmented"] == 2
        assert results["invitations_sent"] == 2

    @pytest.mark.asyncio
    async def test_segmentation_analytics(self, segmentation_worker):
        """Test segmentation analytics generation."""
        # Add test data
        segmentation_worker.segmentation_cache = {
            "group1:user1": ["deal_seekers", "tech_enthusiasts"],
            "group1:user2": ["deal_seekers"]
        }

        segmentation_worker.micro_groups = {
            "micro1": MicroGroup(group_id="micro1", member_count=5),
            "micro2": MicroGroup(group_id="micro2", member_count=3)
        }

        analytics = await segmentation_worker.get_segmentation_analytics()

        assert analytics["cached_segmentations"] == 2
        assert analytics["micro_group_statistics"]["total_micro_groups"] == 2
        assert analytics["micro_group_statistics"]["total_members"] == 8

    def test_segment_removal(self, segmentation_worker):
        """Test user segment removal."""
        segment = UserSegment(segment_id="test_segment", segment_name="Test", tenant_id="tenant_123")
        segmentation_worker.add_user_segment(segment)

        assert "test_segment" in segmentation_worker.user_segments

        segmentation_worker.remove_user_segment("test_segment")

        assert "test_segment" not in segmentation_worker.user_segments

    def test_invitation_message_generation(self, segmentation_worker):
        """Test invitation message generation."""
        segment = UserSegment(
            segment_id="premium_users",
            segment_name="Premium Users",
            tenant_id="tenant_123",
            description="Exclusive premium features"
        )

        micro_group = MicroGroup(
            group_id="micro_123",
            segment_id="premium_users",
            tenant_id="tenant_123",
            group_name="Premium Community"
        )

        message = segmentation_worker._generate_invitation_message(segment, "https://example.com/join")

        assert "Premium Users" in message
        assert "Exclusive premium features" in message
        assert "https://example.com/join" in message

    def test_welcome_message_generation(self, segmentation_worker):
        """Test welcome message generation."""
        micro_group = MicroGroup(
            group_id="micro_123",
            segment_id="premium_users",
            tenant_id="tenant_123"
        )

        message = segmentation_worker._generate_welcome_message(micro_group)

        assert "Welcome" in message
        assert "community" in message.lower()
