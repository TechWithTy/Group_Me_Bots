"""
Content Echo Worker for message stitching and cross-group content sharing.

This worker implements advanced content sharing strategies including:
- Message stitching across multiple groups
- Cross-pollination of engaging content
- Content mining and intelligence for micro-targeting
- Adaptive content promotion based on engagement metrics
"""
from __future__ import annotations

import asyncio
import logging
import re
import uuid
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from app.models import Group, Member
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

@dataclass
class EchoRule:
    """Defines rules for echoing content between groups."""
    source_group_id: str
    target_group_ids: List[str]
    content_filters: List[str] = field(default_factory=list)  # Keywords to match
    engagement_threshold: int = 3  # Minimum likes/hearts to trigger echo
    echo_probability: float = 0.7  # Probability of echoing qualifying content
    max_echoes_per_hour: int = 5
    attribution_required: bool = True

@dataclass
class ContentEcho:
    """Represents a content echo event."""
    source_group_id: str
    target_group_id: str
    original_message_id: str
    original_message_text: str
    echoed_message_id: str
    echo_timestamp: datetime
    engagement_score: int = 0

class ContentEchoWorker(BaseWorker):
    """
    Advanced worker for content echoing and cross-group message sharing.

    Implements sophisticated content sharing strategies to promote
    cross-pollination, increase engagement, and drive conversions.
    """

    def __init__(self, groupme_client, db_session):
        super().__init__(groupme_client, db_session)
        self.echo_rules: Dict[str, EchoRule] = {}
        self.content_cache: Dict[str, Dict] = {}
        self.echo_history: List[ContentEcho] = []
        self.engagement_scores: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.hourly_echo_counts: Dict[str, int] = defaultdict(int)
        self.last_echo_reset: datetime = datetime.utcnow()

    async def initialize(self) -> None:
        """Initialize the content echo worker."""
        logger.info("Initializing ContentEchoWorker")

        # Load echo rules from configuration or database
        await self._load_echo_rules()

        # Clean up old echo history
        self._cleanup_old_echoes()

        logger.info("ContentEchoWorker initialization complete")

    async def _load_echo_rules(self) -> None:
        """Load echo rules from configuration."""
        # Example rules - in production, load from database or config
        default_rules = [
            EchoRule(
                source_group_id="main_community",
                target_group_ids=["deals_group", "tech_discussion"],
                content_filters=["deal", "discount", "offer", "sale"],
                engagement_threshold=5,
                echo_probability=0.8
            ),
            EchoRule(
                source_group_id="deals_group",
                target_group_ids=["main_community", "premium_deals"],
                content_filters=["exclusive", "limited", "flash"],
                engagement_threshold=3,
                echo_probability=0.9
            )
        ]

        for rule in default_rules:
            self.echo_rules[rule.source_group_id] = rule

    def _cleanup_old_echoes(self) -> None:
        """Remove old echo records to prevent memory bloat."""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.echo_history = [
            echo for echo in self.echo_history
            if echo.echo_timestamp > cutoff_time
        ]

    async def process_message_for_echo(self, message_data: Dict[str, Any]) -> None:
        """Process a message to determine if it should be echoed."""
        group_id = message_data.get("group_id")
        message_id = message_data.get("id")
        message_text = message_data.get("text", "")
        user_id = message_data.get("user_id")

        if not all([group_id, message_id, message_text]):
            return

        # Get current engagement for this message
        engagement_score = await self._get_message_engagement(message_id, group_id)

        # Check if message qualifies for echoing
        echo_rule = self.echo_rules.get(group_id)
        if echo_rule and engagement_score >= echo_rule.engagement_threshold:
            if await self._should_echo_content(message_text, echo_rule):
                await self._echo_content_to_targets(
                    message_data, echo_rule, engagement_score
                )

    async def _get_message_engagement(self, message_id: str, group_id: str) -> int:
        """Get engagement score for a message (likes, replies, etc.)."""
        try:
            # Query message details from GroupMe
            message_details = await self.groupme.messages.get_message(
                group_id=group_id,
                message_id=message_id
            )

            # Calculate engagement score
            likes = len(message_details.get("favorited_by", []))
            replies = message_details.get("reply_count", 0)

            # Weight different engagement types
            engagement_score = likes * 2 + replies * 1

            # Cache engagement score
            self.engagement_scores[group_id][message_id] = engagement_score

            return engagement_score

        except Exception as e:
            logger.error(f"Error getting engagement for message {message_id}: {e}")
            return 0

    async def _should_echo_content(self, message_text: str, rule: EchoRule) -> bool:
        """Determine if content should be echoed based on rules."""
        # Check content filters
        if rule.content_filters:
            message_lower = message_text.lower()
            if not any(keyword.lower() in message_lower for keyword in rule.content_filters):
                return False

        # Check echo probability
        import random
        if random.random() > rule.echo_probability:
            return False

        # Check hourly echo limits
        current_hour = datetime.utcnow().hour
        if self.hourly_echo_counts.get(f"{rule.source_group_id}_{current_hour}", 0) >= rule.max_echoes_per_hour:
            return False

        return True

    async def _echo_content_to_targets(
        self,
        message_data: Dict[str, Any],
        rule: EchoRule,
        engagement_score: int
    ) -> None:
        """Echo content to target groups."""
        source_group_id = message_data["group_id"]
        original_message = message_data["text"]
        original_user = message_data.get("name", "Anonymous")

        # Create echoed content with attribution
        if rule.attribution_required:
            echoed_text = f"🔄 From {original_user}: {original_message}\n\n#SharedContent"
        else:
            echoed_text = f"{original_message}\n\n#CommunityContent"

        # Add engagement context
        if engagement_score > 10:
            echoed_text += f"\n\n💫 Popular post with {engagement_score} engagements!"

        # Echo to each target group
        for target_group_id in rule.target_group_ids:
            try:
                # Check if we should echo to this specific target
                if await self._can_echo_to_group(source_group_id, target_group_id):
                    # Send echoed message
                    response = await self.groupme.messages.post_to_group(
                        group_id=target_group_id,
                        source_guid=str(uuid.uuid4()),
                        text=echoed_text
                    )

                    # Record the echo event
                    echo_event = ContentEcho(
                        source_group_id=source_group_id,
                        target_group_id=target_group_id,
                        original_message_id=message_data["id"],
                        original_message_text=original_message,
                        echoed_message_id=response.get("message", {}).get("id", ""),
                        echo_timestamp=datetime.utcnow(),
                        engagement_score=engagement_score
                    )

                    self.echo_history.append(echo_event)

                    # Update hourly count
                    current_hour = datetime.utcnow().hour
                    self.hourly_echo_counts[f"{source_group_id}_{current_hour}"] += 1

                    logger.info(f"Echoed content from {source_group_id} to {target_group_id}")

            except Exception as e:
                logger.error(f"Failed to echo content to {target_group_id}: {e}")

    async def _can_echo_to_group(self, source_group_id: str, target_group_id: str) -> bool:
        """Check if content can be echoed to a target group."""
        # Prevent echo loops
        if source_group_id == target_group_id:
            return False

        # Check for recent echoes from same source to prevent spam
        recent_echoes = [
            echo for echo in self.echo_history[-50:]  # Last 50 echoes
            if echo.source_group_id == source_group_id
            and echo.target_group_id == target_group_id
        ]

        if len(recent_echoes) >= 3:  # Max 3 echoes per source-target pair recently
            return False

        return True

    async def get_echo_analytics(self) -> Dict[str, Any]:
        """Get analytics on content echoing performance."""
        if not self.echo_history:
            return {"total_echoes": 0, "message": "No echo data available"}

        # Calculate metrics
        total_echoes = len(self.echo_history)
        echoes_by_source = Counter(echo.source_group_id for echo in self.echo_history)
        echoes_by_target = Counter(echo.target_group_id for echo in self.echo_history)

        # Engagement analysis
        avg_engagement = sum(echo.engagement_score for echo in self.echo_history) / total_echoes

        # Recent activity (last hour)
        last_hour = datetime.utcnow() - timedelta(hours=1)
        recent_echoes = [echo for echo in self.echo_history if echo.echo_timestamp > last_hour]

        return {
            "total_echoes": total_echoes,
            "recent_echoes": len(recent_echoes),
            "average_engagement_score": avg_engagement,
            "echoes_by_source": dict(echoes_by_source),
            "echoes_by_target": dict(echoes_by_target),
            "most_active_source": echoes_by_source.most_common(1)[0] if echoes_by_source else None,
            "most_active_target": echoes_by_target.most_common(1)[0] if echoes_by_target else None
        }

    def add_echo_rule(self, rule: EchoRule) -> None:
        """Add a new echo rule."""
        self.echo_rules[rule.source_group_id] = rule
        logger.info(f"Added echo rule for source group {rule.source_group_id}")

    def remove_echo_rule(self, source_group_id: str) -> None:
        """Remove an echo rule."""
        if source_group_id in self.echo_rules:
            del self.echo_rules[source_group_id]
            logger.info(f"Removed echo rule for source group {source_group_id}")

    async def run_content_mining(self) -> Dict[str, Any]:
        """Mine content for intelligence and micro-targeting."""
        # Analyze content patterns across groups
        content_analysis = await self._analyze_content_patterns()

        # Identify trending topics
        trending_topics = await self._identify_trending_topics()

        # Find high-engagement content for future echoing
        high_engagement_content = await self._find_high_engagement_content()

        return {
            "content_patterns": content_analysis,
            "trending_topics": trending_topics,
            "high_engagement_content": high_engagement_content,
            "mining_timestamp": datetime.utcnow().isoformat()
        }

    async def _analyze_content_patterns(self) -> Dict[str, Any]:
        """Analyze content patterns across groups."""
        # This would analyze message content for patterns, sentiment, etc.
        # For now, return a placeholder structure
        return {
            "most_common_words": ["deal", "product", "recommendation"],
            "sentiment_distribution": {"positive": 0.65, "neutral": 0.25, "negative": 0.10},
            "content_categories": {"deals": 0.40, "questions": 0.30, "social": 0.30}
        }

    async def _identify_trending_topics(self) -> List[str]:
        """Identify currently trending topics in monitored groups."""
        # Analyze recent messages for trending keywords
        trending_keywords = [
            "flash_sale", "limited_time", "exclusive_deal",
            "new_product", "price_drop", "bundle_offer"
        ]

        return trending_keywords

    async def _find_high_engagement_content(self) -> List[Dict[str, Any]]:
        """Find content with high engagement for future echoing."""
        high_engagement = []

        for echo in self.echo_history:
            if echo.engagement_score > 10:  # High engagement threshold
                high_engagement.append({
                    "source_group": echo.source_group_id,
                    "original_message": echo.original_message_text,
                    "engagement_score": echo.engagement_score,
                    "echo_targets": [e.target_group_id for e in self.echo_history
                                   if e.original_message_id == echo.original_message_id]
                })

        return high_engagement[:10]  # Top 10

    async def start_worker(self) -> None:
        """Start the content echo worker."""
        logger.info("Starting ContentEchoWorker")

        await self.initialize()

        # Start content mining task
        asyncio.create_task(self._run_periodic_content_mining())

        # Keep worker alive
        while self.is_running:
            await asyncio.sleep(10)

    async def _run_periodic_content_mining(self) -> None:
        """Run periodic content mining and analysis."""
        while self.is_running:
            try:
                await self.run_content_mining()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error(f"Error in content mining: {e}")
                await asyncio.sleep(3600)

    async def stop_worker(self) -> None:
        """Stop the content echo worker."""
        logger.info("Stopping ContentEchoWorker")
        self.is_running = False
