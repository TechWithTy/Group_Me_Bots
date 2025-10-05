"""
Segmentation Worker for automatic group segmentation and micro-targeting.

This worker implements sophisticated user segmentation, micro-group creation,
and targeted messaging strategies based on user behavior and interests.
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from app.models import Group, Member
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

@dataclass
class UserSegment:
    """Represents a user segment with criteria and metadata."""
    segment_id: str
    segment_name: str
    tenant_id: str

    # Segmentation criteria
    keywords: List[str] = field(default_factory=list)
    engagement_threshold: float = 0.5
    activity_patterns: List[str] = field(default_factory=list)

    # Segment metadata
    description: str = ""
    target_size: int = 100
    is_active: bool = True

@dataclass
class MicroGroup:
    """Represents a micro-group created for targeted messaging."""
    group_id: str
    parent_group_id: str
    segment_id: str
    tenant_id: str

    # Group metadata
    group_name: str = ""
    description: str = ""
    member_count: int = 0
    max_members: int = 100

    # Targeting configuration
    auto_invite: bool = True
    invitation_message: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

class SegmentationWorker(BaseWorker):
    """
    Advanced worker for user segmentation and micro-group management.

    Implements automatic user segmentation based on behavior patterns,
    creates micro-groups for targeted messaging, and manages
    invitation workflows for optimal group composition.
    """

    def __init__(self, groupme_client, db_session):
        super().__init__(groupme_client, db_session)
        self.user_segments: Dict[str, UserSegment] = {}
        self.micro_groups: Dict[str, MicroGroup] = {}
        self.segmentation_cache: Dict[str, List[str]] = defaultdict(list)
        self.invitation_queue: asyncio.Queue = asyncio.Queue()

    async def initialize(self) -> None:
        """Initialize the segmentation worker."""
        logger.info("Initializing SegmentationWorker")

        # Load user segments
        await self._load_user_segments()

        # Initialize micro-group tracking
        await self._initialize_micro_groups()

        # Start invitation processing
        asyncio.create_task(self._process_invitations())

        logger.info("SegmentationWorker initialization complete")

    async def _load_user_segments(self) -> None:
        """Load user segmentation rules."""
        # Default segments - in production, load from database
        default_segments = [
            UserSegment(
                segment_id="deal_seekers",
                segment_name="Deal Seekers",
                tenant_id="default",
                keywords=["deal", "discount", "sale", "offer", "coupon", "promo"],
                engagement_threshold=0.6,
                description="Users actively looking for deals and discounts"
            ),
            UserSegment(
                segment_id="tech_enthusiasts",
                segment_name="Tech Enthusiasts",
                tenant_id="default",
                keywords=["tech", "programming", "software", "AI", "computer", "gadget"],
                engagement_threshold=0.7,
                description="Users interested in technology and gadgets"
            ),
            UserSegment(
                segment_id="high_engagement",
                segment_name="High Engagement Users",
                tenant_id="default",
                engagement_threshold=0.8,
                activity_patterns=["daily_posts", "multiple_likes"],
                description="Highly active community members"
            )
        ]

        for segment in default_segments:
            self.user_segments[segment.segment_id] = segment

    async def _initialize_micro_groups(self) -> None:
        """Initialize tracking of existing micro-groups."""
        # In production, load from database
        # For now, initialize empty
        pass

    async def analyze_user_for_segmentation(self, user_id: str, group_id: str, message_text: str) -> List[str]:
        """Analyze a user message for segmentation opportunities."""
        matching_segments = []

        # Get user's recent activity
        user_activity = await self._get_user_activity(user_id, group_id, days=7)

        # Check each segment for matches
        for segment in self.user_segments.values():
            if await self._user_matches_segment(user_id, group_id, message_text, user_activity, segment):
                matching_segments.append(segment.segment_id)

        # Cache segmentation results
        cache_key = f"{group_id}:{user_id}"
        self.segmentation_cache[cache_key] = matching_segments

        return matching_segments

    async def _get_user_activity(self, user_id: str, group_id: str, days: int = 7) -> Dict[str, Any]:
        """Get user's activity metrics for segmentation."""
        # In production, query from database
        # For now, return mock data
        return {
            "message_count": 5,
            "like_count": 3,
            "reply_count": 2,
            "engagement_score": 0.7,
            "activity_pattern": "regular"
        }

    async def _user_matches_segment(self, user_id: str, group_id: str, message_text: str, user_activity: Dict[str, Any], segment: UserSegment) -> bool:
        """Check if user matches a specific segment."""
        # Check keyword matches
        message_lower = message_text.lower()
        keyword_matches = any(
            keyword.lower() in message_lower
            for keyword in segment.keywords
        )

        # Check engagement threshold
        engagement_score = user_activity.get("engagement_score", 0)
        engagement_match = engagement_score >= segment.engagement_threshold

        # Check activity patterns
        activity_pattern = user_activity.get("activity_pattern", "")
        pattern_match = not segment.activity_patterns or activity_pattern in segment.activity_patterns

        return (keyword_matches or engagement_match) and pattern_match

    async def create_micro_group(self, parent_group_id: str, segment_id: str, custom_config: Dict[str, Any] = None) -> str:
        """Create a micro-group for a specific user segment."""
        segment = self.user_segments.get(segment_id)
        if not segment:
            raise ValueError(f"Segment {segment_id} not found")

        # Generate unique group name
        group_name = f"{segment.segment_name} - {parent_group_id[:8]}"

        # Create GroupMe group
        try:
            group_response = await self.groupme.groups.create_group(
                name=group_name,
                description=segment.description,
                share=True  # Enable sharing for invitations
            )

            group_id = group_response.get("id")
            share_url = group_response.get("share_url")

            if not group_id:
                raise Exception("Failed to create group")

            # Create micro-group record
            micro_group = MicroGroup(
                group_id=group_id,
                parent_group_id=parent_group_id,
                segment_id=segment_id,
                tenant_id=segment.tenant_id,
                group_name=group_name,
                description=f"Micro-group for {segment.segment_name} segment",
                invitation_message=self._generate_invitation_message(segment, share_url)
            )

            self.micro_groups[group_id] = micro_group

            logger.info(f"Created micro-group {group_id} for segment {segment_id}")

            return group_id

        except Exception as e:
            logger.error(f"Failed to create micro-group: {e}")
            raise

    def _generate_invitation_message(self, segment: UserSegment, share_url: str) -> str:
        """Generate invitation message for a segment."""
        return (
            f"🎯 Exclusive {segment.segment_name} Community!\n\n"
            f"Join our specialized group for {segment.description.lower()}:\n"
            f"{share_url}\n\n"
            "Limited spots available - first come, first served!"
        )

    async def invite_user_to_micro_group(self, user_id: str, micro_group_id: str) -> bool:
        """Invite a user to a micro-group."""
        micro_group = self.micro_groups.get(micro_group_id)
        if not micro_group:
            return False

        # Check if group is at capacity
        if micro_group.member_count >= micro_group.max_members:
            logger.warning(f"Micro-group {micro_group_id} is at capacity")
            return False

        try:
            # Add user to GroupMe group
            await self.groupme.groups.add_members(
                group_id=micro_group.group_id,
                members=[{"user_id": user_id}]
            )

            # Update member count
            micro_group.member_count += 1

            # Queue personalized welcome message
            await self.invitation_queue.put({
                "user_id": user_id,
                "group_id": micro_group.group_id,
                "segment_id": micro_group.segment_id,
                "welcome_message": self._generate_welcome_message(micro_group)
            })

            logger.info(f"Invited user {user_id} to micro-group {micro_group_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to invite user {user_id} to micro-group {micro_group_id}: {e}")
            return False

    def _generate_welcome_message(self, micro_group: MicroGroup) -> str:
        """Generate welcome message for new micro-group member."""
        segment = self.user_segments.get(micro_group.segment_id)
        if not segment:
            return "Welcome to our exclusive community!"

        return (
            f"Welcome to the {segment.segment_name} group! 🎉\n\n"
            f"This is a curated space for {segment.description.lower()}.\n\n"
            "Feel free to share your thoughts, ask questions, and connect with like-minded people!"
        )

    async def run_automatic_segmentation(self) -> Dict[str, Any]:
        """Run automatic segmentation analysis and create micro-groups as needed."""
        # Get all active users and analyze for segmentation
        active_groups = await self.get_active_groups()

        segmentation_results = {
            "total_users_analyzed": 0,
            "users_segmented": 0,
            "micro_groups_created": 0,
            "invitations_sent": 0,
            "segment_breakdown": {}
        }

        for group in active_groups:
            group_segmentation = await self._segment_group_users(group.id)
            segmentation_results["total_users_analyzed"] += group_segmentation["users_analyzed"]
            segmentation_results["users_segmented"] += group_segmentation["users_segmented"]
            segmentation_results["micro_groups_created"] += group_segmentation["micro_groups_created"]
            segmentation_results["invitations_sent"] += group_segmentation["invitations_sent"]

            # Update segment breakdown
            for segment_id, count in group_segmentation["segment_counts"].items():
                segmentation_results["segment_breakdown"][segment_id] = (
                    segmentation_results["segment_breakdown"].get(segment_id, 0) + count
                )

        return segmentation_results

    async def _segment_group_users(self, group_id: str) -> Dict[str, Any]:
        """Segment users in a specific group."""
        # Get recent group messages
        recent_messages = await self._get_recent_group_messages(group_id, days=7)

        results = {
            "users_analyzed": 0,
            "users_segmented": 0,
            "micro_groups_created": 0,
            "invitations_sent": 0,
            "segment_counts": defaultdict(int)
        }

        # Analyze each message for segmentation opportunities
        for message in recent_messages:
            user_id = message.get("user_id")
            if not user_id:
                continue

            results["users_analyzed"] += 1

            # Check if user matches any segments
            matching_segments = await self.analyze_user_for_segmentation(
                user_id, group_id, message.get("text", "")
            )

            for segment_id in matching_segments:
                results["segment_counts"][segment_id] += 1

                # Check if we need to create/invite to micro-group
                micro_group_id = await self._get_or_create_micro_group(group_id, segment_id)

                if micro_group_id:
                    if await self.invite_user_to_micro_group(user_id, micro_group_id):
                        results["invitations_sent"] += 1

        return results

    async def _get_or_create_micro_group(self, parent_group_id: str, segment_id: str) -> Optional[str]:
        """Get existing micro-group or create new one."""
        # Check if micro-group already exists
        for micro_group in self.micro_groups.values():
            if (micro_group.parent_group_id == parent_group_id and
                micro_group.segment_id == segment_id):
                return micro_group.group_id

        # Create new micro-group if needed
        try:
            micro_group_id = await self.create_micro_group(parent_group_id, segment_id)
            return micro_group_id
        except Exception as e:
            logger.error(f"Failed to create micro-group for {segment_id}: {e}")
            return None

    async def _get_recent_group_messages(self, group_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent messages from a group."""
        # In production, query GroupMe API for messages
        # For now, return mock data
        return [
            {"user_id": f"user_{i}", "text": f"Sample message {i}"}
            for i in range(10)
        ]

    async def get_segmentation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive segmentation analytics."""
        # Segment distribution
        segment_users = defaultdict(int)
        for cache_key, segments in self.segmentation_cache.items():
            for segment_id in segments:
                segment_users[segment_id] += 1

        # Micro-group statistics
        micro_group_stats = {
            "total_micro_groups": len(self.micro_groups),
            "total_members": sum(mg.member_count for mg in self.micro_groups.values()),
            "avg_members_per_group": (
                sum(mg.member_count for mg in self.micro_groups.values()) / len(self.micro_groups)
                if self.micro_groups else 0
            )
        }

        # Invitation success rate
        total_invitations = sum(
            len(queue_item) for queue_item in [self.invitation_queue._queue]
            if hasattr(self.invitation_queue, '_queue')
        )

        return {
            "segment_distribution": dict(segment_users),
            "micro_group_statistics": micro_group_stats,
            "cached_segmentations": len(self.segmentation_cache),
            "pending_invitations": self.invitation_queue.qsize() if hasattr(self.invitation_queue, 'qsize') else 0,
            "last_updated": datetime.utcnow().isoformat()
        }

    async def _process_invitations(self) -> None:
        """Process queued invitations."""
        while self.is_running:
            try:
                if not self.invitation_queue.empty():
                    invitation = await self.invitation_queue.get()

                    # Send welcome message to new micro-group member
                    await self._send_micro_group_welcome(invitation)

                    await asyncio.sleep(1)  # Rate limiting

                else:
                    await asyncio.sleep(5)  # Wait before checking again

            except Exception as e:
                logger.error(f"Error processing invitation: {e}")
                await asyncio.sleep(5)

    async def _send_micro_group_welcome(self, invitation: Dict[str, Any]) -> None:
        """Send welcome message to new micro-group member."""
        try:
            welcome_message = invitation.get("welcome_message", "Welcome!")

            await self.groupme.messages.post_to_group(
                group_id=invitation["group_id"],
                source_guid=str(uuid.uuid4()),
                text=welcome_message
            )

            logger.debug(f"Sent welcome message for invitation: {invitation['user_id']}")

        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")

    def add_user_segment(self, segment: UserSegment) -> None:
        """Add a new user segment."""
        self.user_segments[segment.segment_id] = segment
        logger.info(f"Added user segment: {segment.segment_name}")

    def remove_user_segment(self, segment_id: str) -> None:
        """Remove a user segment."""
        if segment_id in self.user_segments:
            del self.user_segments[segment_id]
            logger.info(f"Removed user segment: {segment_id}")

    async def start_worker(self) -> None:
        """Start the segmentation worker."""
        logger.info("Starting SegmentationWorker")

        await self.initialize()

        # Start automatic segmentation
        asyncio.create_task(self._run_automatic_segmentation())

        # Keep worker alive
        while self.is_running:
            await asyncio.sleep(10)

    async def _run_automatic_segmentation(self) -> None:
        """Run automatic segmentation analysis periodically."""
        while self.is_running:
            try:
                # Run segmentation analysis
                segmentation_results = await self.run_automatic_segmentation()

                logger.info(f"Segmentation cycle completed: {segmentation_results}")

                # Clean up old cache
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                keys_to_remove = [
                    key for key, segments in self.segmentation_cache.items()
                    if segments  # Only remove if empty
                ]
                for key in keys_to_remove:
                    del self.segmentation_cache[key]

                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                logger.error(f"Error in automatic segmentation: {e}")
                await asyncio.sleep(3600)

    async def stop_worker(self) -> None:
        """Stop the segmentation worker."""
        logger.info("Stopping SegmentationWorker")

        # Cancel invitation processing
        if hasattr(self.invitation_queue, 'task'):
            self.invitation_queue.task.cancel()

        self.is_running = False
