"""
Engagement Worker for adaptive frequency control and soft opt-in mechanisms.

This worker implements sophisticated engagement tracking and adaptive messaging strategies
including burst mode control, soft opt-ins, and engagement-based promotions.
"""
from __future__ import annotations

import asyncio
import logging
import random
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter

import uuid

from app.models import Group, Member
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

@dataclass
class EngagementProfile:
    """Tracks engagement profile for a user."""
    user_id: str
    group_id: str
    tenant_id: str

    # Engagement metrics
    message_count: int = 0
    like_count: int = 0
    reply_count: int = 0
    last_activity: datetime = field(default_factory=datetime.utcnow)

    # Calculated scores
    engagement_score: float = 0.0
    activity_level: str = "low"  # low, medium, high, very_high

    # Opt-in status
    soft_opted_in: bool = False
    explicit_opt_in: bool = False

@dataclass
class AdaptiveFrequencyRule:
    """Rules for adaptive message frequency."""
    group_id: str
    base_frequency_per_hour: float = 1.0
    max_frequency_per_hour: float = 5.0
    engagement_threshold: float = 0.5

    # Time-based adjustments
    peak_hours: List[int] = field(default_factory=lambda: [9, 10, 11, 14, 15, 16, 19, 20, 21])
    quiet_hours: List[int] = field(default_factory=lambda: [2, 3, 4, 5, 6])

    # Content type multipliers
    promotional_multiplier: float = 0.8
    informational_multiplier: float = 1.2
    urgent_multiplier: float = 1.5

@dataclass
class GamificationLevel:
    """Represents a user's gamification level and privileges."""
    level: str
    name: str
    required_engagement_score: float
    privileges: List[str]
    unlock_message: str

@dataclass
class OnboardingFlow:
    """Defines an onboarding flow for new users."""
    flow_id: str
    welcome_message: str
    preference_questions: List[str]
    follow_up_delay_hours: int = 24
    premium_invite_threshold: float = 0.7

@dataclass
class PhantomMention:
    """Represents a phantom mention campaign."""
    mention_id: str
    target_criteria: Dict[str, Any]  # active_only, inactive_days, etc.
    message_template: str
    max_mentions_per_cycle: int = 50

class EngagementWorker(BaseWorker):
    """
    Advanced worker for engagement tracking and adaptive messaging.

    Implements adaptive frequency control, soft opt-in mechanisms,
    and engagement-based promotion strategies.
    """

    def __init__(self, groupme_client, db_session):
        super().__init__(groupme_client, db_session)
        self.engagement_profiles: Dict[str, EngagementProfile] = {}
        self.frequency_rules: Dict[str, AdaptiveFrequencyRule] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.engagement_signals: Dict[str, List[str]] = defaultdict(list)
        self.burst_mode_active: Dict[str, bool] = {}
        self.last_frequency_check: Dict[str, datetime] = {}

        # Advanced features
        self.gamification_levels: Dict[str, GamificationLevel] = {}
        self.onboarding_flows: Dict[str, OnboardingFlow] = {}
        self.phantom_mentions: Dict[str, PhantomMention] = {}
        self.shadow_mode_active: Dict[str, bool] = {}
        self.context_triggers: Dict[str, List[str]] = defaultdict(list)

    async def initialize(self) -> None:
        """Initialize the engagement worker."""
        logger.info("Initializing EngagementWorker")

        # Load frequency rules
        await self._load_frequency_rules()

        # Initialize engagement tracking
        await self._initialize_engagement_tracking()

        logger.info("EngagementWorker initialization complete")

    async def _load_frequency_rules(self) -> None:
        """Load adaptive frequency rules."""
        # Default rules - in production, load from database
        default_rules = [
            AdaptiveFrequencyRule(
                group_id="main_community",
                base_frequency_per_hour=2.0,
                max_frequency_per_hour=8.0,
                engagement_threshold=0.6
            ),
            AdaptiveFrequencyRule(
                group_id="deals_group",
                base_frequency_per_hour=3.0,
                max_frequency_per_hour=12.0,
                engagement_threshold=0.7,
                promotional_multiplier=1.2
            )
        ]

        for rule in default_rules:
            self.frequency_rules[rule.group_id] = rule

    async def _initialize_engagement_tracking(self) -> None:
        """Initialize engagement tracking for active groups."""
        groups = await self.get_active_groups()

        for group in groups:
            # Get recent group activity
            recent_messages = await self._get_recent_group_activity(group.id, hours=24)

            # Build engagement profiles for active users
            for message in recent_messages:
                user_id = message.get("user_id")
                if user_id:
                    await self._update_engagement_profile(user_id, group.id, group.tenant_id)

    async def track_user_engagement(self, message_data: Dict[str, Any]) -> None:
        """Track user engagement from a message."""
        user_id = message_data.get("user_id")
        group_id = message_data.get("group_id")
        tenant_id = message_data.get("tenant_id", "")  # Assuming tenant_id is available

        if not all([user_id, group_id]):
            return

        # Update engagement profile
        await self._update_engagement_profile(user_id, group_id, tenant_id)

        # Check for soft opt-in signals
        await self._check_soft_opt_in_signals(user_id, message_data.get("text", ""), group_id)

        # Update group engagement metrics
        await self._update_group_engagement_metrics(group_id)

    async def _update_engagement_profile(self, user_id: str, group_id: str, tenant_id: str) -> None:
        """Update engagement profile for a user."""
        profile_key = f"{tenant_id}:{group_id}:{user_id}"

        if profile_key not in self.engagement_profiles:
            self.engagement_profiles[profile_key] = EngagementProfile(
                user_id=user_id,
                group_id=group_id,
                tenant_id=tenant_id
            )

        profile = self.engagement_profiles[profile_key]

        # Update activity metrics
        profile.message_count += 1
        profile.last_activity = datetime.utcnow()

        # Recalculate engagement score
        profile.engagement_score = self._calculate_engagement_score(profile)

        # Update activity level
        profile.activity_level = self._determine_activity_level(profile.engagement_score)

        logger.debug(f"Updated engagement for user {user_id}: score={profile.engagement_score}")

    def _calculate_engagement_score(self, profile: EngagementProfile) -> float:
        """Calculate engagement score based on activity metrics."""
        # Weighted scoring algorithm
        message_weight = 0.4
        recency_weight = 0.3
        consistency_weight = 0.3

        # Message activity score (0-1)
        message_score = min(profile.message_count / 10, 1.0)  # Normalize to 10+ messages

        # Recency score (0-1, decays over time)
        hours_since_activity = (datetime.utcnow() - profile.last_activity).total_seconds() / 3600
        recency_score = max(0, 1.0 - (hours_since_activity / 24))  # Decays over 24 hours

        # Consistency score (based on activity pattern)
        # For now, use a simple consistency metric
        consistency_score = 0.5  # Placeholder

        total_score = (
            message_score * message_weight +
            recency_score * recency_weight +
            consistency_score * consistency_weight
        )

        return min(total_score, 1.0)

    def _determine_activity_level(self, engagement_score: float) -> str:
        """Determine activity level based on engagement score."""
        if engagement_score >= 0.8:
            return "very_high"
        elif engagement_score >= 0.6:
            return "high"
        elif engagement_score >= 0.4:
            return "medium"
        else:
            return "low"

    async def _check_soft_opt_in_signals(self, user_id: str, message_text: str, group_id: str) -> None:
        """Check for soft opt-in signals in user messages."""
        profile_key = f"{group_id}:{user_id}"  # Simplified key for this context
        profile = self.engagement_profiles.get(profile_key)

        if not profile:
            return

        # Define soft opt-in trigger phrases
        opt_in_signals = [
            "interested", "want to know more", "tell me more",
            "how do I", "where can I", "looking for",
            "need help with", "recommend", "suggest"
        ]

        message_lower = message_text.lower()

        # Check if message contains opt-in signals
        if any(signal in message_lower for signal in opt_in_signals):
            # Check if user is already engaged
            if profile.engagement_score > 0.5 and not profile.soft_opted_in:
                profile.soft_opted_in = True
                self.engagement_signals[group_id].append(f"Soft opt-in detected for user {user_id}")

                logger.info(f"Soft opt-in detected for user {user_id} in group {group_id}")

                # Trigger soft opt-in welcome or promotion
                await self._handle_soft_opt_in(user_id, group_id)

    async def _handle_soft_opt_in(self, user_id: str, group_id: str) -> None:
        """Handle soft opt-in by sending targeted promotion."""
        # Get user's engagement profile
        profile_key = f"{group_id}:{user_id}"
        profile = self.engagement_profiles.get(profile_key)

        if not profile:
            return

        # Generate personalized soft opt-in message
        if profile.activity_level in ["high", "very_high"]:
            opt_in_message = (
                "Thanks for being active in our community! 🎉\n\n"
                "I noticed you're interested in our discussions. "
                "Want to join our exclusive deals group for special offers?"
            )
        else:
            opt_in_message = (
                "I see you're interested in our content! "
                "Would you like personalized recommendations and early access to deals?"
            )

        try:
            # Send private message or group message
            await self.groupme.messages.post_to_group(
                group_id=group_id,
                source_guid=str(uuid.uuid4()),
                text=opt_in_message
            )

            logger.info(f"Sent soft opt-in message to user {user_id}")

        except Exception as e:
            logger.error(f"Failed to send soft opt-in message: {e}")

    async def _update_group_engagement_metrics(self, group_id: str) -> None:
        """Update overall engagement metrics for a group."""
        # Get all engagement profiles for this group
        group_profiles = [
            profile for profile in self.engagement_profiles.values()
            if profile.group_id == group_id
        ]

        if not group_profiles:
            return

        # Calculate group-level metrics
        total_engagement = sum(profile.engagement_score for profile in group_profiles)
        avg_engagement = total_engagement / len(group_profiles)

        active_users = len([p for p in group_profiles if p.activity_level in ["high", "very_high"]])

        # Update burst mode status
        frequency_rule = self.frequency_rules.get(group_id)
        if frequency_rule and avg_engagement > frequency_rule.engagement_threshold:
            self.burst_mode_active[group_id] = True
        else:
            self.burst_mode_active[group_id] = False

    def get_adaptive_frequency(self, group_id: str, content_type: str = "general") -> float:
        """Get adaptive message frequency for a group."""
        frequency_rule = self.frequency_rules.get(group_id)
        if not frequency_rule:
            return 1.0  # Default frequency

        # Base frequency
        base_frequency = frequency_rule.base_frequency_per_hour

        # Adjust for engagement level
        group_profiles = [
            profile for profile in self.engagement_profiles.values()
            if profile.group_id == group_id
        ]

        if group_profiles:
            avg_engagement = sum(p.engagement_score for p in group_profiles) / len(group_profiles)

            # Increase frequency for high engagement
            if avg_engagement > 0.7:
                frequency_multiplier = 1.5
            elif avg_engagement > 0.5:
                frequency_multiplier = 1.2
            else:
                frequency_multiplier = 0.8

            base_frequency *= frequency_multiplier

        # Apply content type multiplier
        if content_type == "promotional":
            base_frequency *= frequency_rule.promotional_multiplier
        elif content_type == "informational":
            base_frequency *= frequency_rule.informational_multiplier
        elif content_type == "urgent":
            base_frequency *= frequency_rule.urgent_multiplier

        # Apply burst mode
        if self.burst_mode_active.get(group_id, False):
            base_frequency *= 1.3

        # Cap at maximum frequency
        return min(base_frequency, frequency_rule.max_frequency_per_hour)

    async def should_send_message(self, group_id: str, content_type: str = "general") -> bool:
        """Determine if a message should be sent based on adaptive frequency."""
        current_time = datetime.utcnow()
        frequency_rule = self.frequency_rules.get(group_id)

        if not frequency_rule:
            return True

        # Check time-based restrictions
        current_hour = current_time.hour
        if current_hour in frequency_rule.quiet_hours:
            return False

        # Check hourly message limit
        last_check = self.last_frequency_check.get(group_id, current_time - timedelta(hours=1))
        hours_since_check = (current_time - last_check).total_seconds() / 3600

        if hours_since_check < 1.0:  # Check every hour
            return False

        # Calculate if we should send based on adaptive frequency
        adaptive_frequency = self.get_adaptive_frequency(group_id, content_type)
        messages_this_hour = self._get_messages_sent_this_hour(group_id)

        # Simple probability-based sending
        send_probability = min(adaptive_frequency - messages_this_hour, 1.0)

        self.last_frequency_check[group_id] = current_time

        return random.random() < send_probability

    def _get_messages_sent_this_hour(self, group_id: str) -> int:
        """Get number of messages sent to a group this hour."""
        current_hour = datetime.utcnow().hour
        # In a real implementation, track actual sent messages
        # For now, return a placeholder
        return 0

    async def get_engagement_analytics(self) -> Dict[str, Any]:
        """Get comprehensive engagement analytics."""
        if not self.engagement_profiles:
            return {"total_users": 0, "message": "No engagement data available"}

        # Aggregate metrics
        total_users = len(self.engagement_profiles)
        active_users = len([p for p in self.engagement_profiles.values() if p.activity_level in ["high", "very_high"]])
        soft_opted_in_users = len([p for p in self.engagement_profiles.values() if p.soft_opted_in])

        # Engagement distribution
        activity_levels = Counter(p.activity_level for p in self.engagement_profiles.values())

        # Group-level metrics
        group_metrics = {}
        for group_id in set(p.group_id for p in self.engagement_profiles.values()):
            group_profiles = [p for p in self.engagement_profiles.values() if p.group_id == group_id]
            group_metrics[group_id] = {
                "total_users": len(group_profiles),
                "avg_engagement_score": sum(p.engagement_score for p in group_profiles) / len(group_profiles),
                "active_users": len([p for p in group_profiles if p.activity_level in ["high", "very_high"]]),
                "burst_mode": self.burst_mode_active.get(group_id, False)
            }

        return {
            "total_users_tracked": total_users,
            "active_users": active_users,
            "soft_opted_in_users": soft_opted_in_users,
            "activity_distribution": dict(activity_levels),
            "group_metrics": group_metrics,
            "burst_mode_groups": [gid for gid, active in self.burst_mode_active.items() if active]
        }

    async def trigger_engagement_campaign(self, group_id: str, campaign_type: str) -> None:
        """Trigger an engagement-based campaign."""
        if campaign_type == "re_engagement":
            await self._trigger_re_engagement_campaign(group_id)
        elif campaign_type == "upsell":
            await self._trigger_upsell_campaign(group_id)

    async def _trigger_re_engagement_campaign(self, group_id: str) -> None:
        """Trigger campaign to re-engage inactive users."""
        # Find inactive users in the group
        inactive_users = [
            profile.user_id for profile in self.engagement_profiles.values()
            if profile.group_id == group_id and profile.activity_level == "low"
        ]

        if inactive_users:
            re_engagement_message = (
                "We've missed seeing you around! 👋\n\n"
                "Here are some recent highlights from our community:\n"
                "• Exclusive deals and discounts\n"
                "• Product recommendations\n"
                "• Community discussions\n\n"
                "Join the conversation - we'd love to hear from you!"
            )

            try:
                await self.groupme.messages.post_to_group(
                    group_id=group_id,
                    source_guid=str(uuid.uuid4()),
                    text=re_engagement_message
                )

                logger.info(f"Sent re-engagement message to {len(inactive_users)} users in group {group_id}")

            except Exception as e:
                logger.error(f"Failed to send re-engagement message: {e}")

    async def _trigger_upsell_campaign(self, group_id: str) -> None:
        """Trigger upsell campaign for engaged users."""
        # Find highly engaged users
        engaged_users = [
            profile.user_id for profile in self.engagement_profiles.values()
            if profile.group_id == group_id and profile.activity_level in ["high", "very_high"]
        ]

        if engaged_users:
            upsell_message = (
                "Thank you for being such an active community member! 🌟\n\n"
                "As a token of appreciation, you're eligible for our premium membership:\n"
                "• Exclusive early access to deals\n"
                "• Priority support\n"
                "• Advanced features\n\n"
                "DM me 'premium' to learn more!"
            )

            try:
                await self.groupme.messages.post_to_group(
                    group_id=group_id,
                    source_guid=str(uuid.uuid4()),
                    text=upsell_message
                )

                logger.info(f"Sent upsell message to {len(engaged_users)} engaged users in group {group_id}")

            except Exception as e:
                logger.error(f"Failed to send upsell message: {e}")

    async def start_worker(self) -> None:
        """Start the engagement worker."""
        logger.info("Starting EngagementWorker")

        await self.initialize()

        # Start engagement tracking
        asyncio.create_task(self._run_engagement_tracking())

        # Keep worker alive
        while self.is_running:
            await asyncio.sleep(10)

    async def _run_engagement_tracking(self) -> None:
        """Run periodic engagement analysis and updates."""
        while self.is_running:
            try:
                # Update engagement metrics
                await self._update_all_engagement_metrics()

                # Check for campaign triggers
                await self._check_campaign_triggers()

                await asyncio.sleep(300)  # Run every 5 minutes

            except Exception as e:
                logger.error(f"Error in engagement tracking: {e}")
                await asyncio.sleep(300)

    async def _update_all_engagement_metrics(self) -> None:
        """Update engagement metrics for all tracked users."""
        for profile in self.engagement_profiles.values():
            # Recalculate engagement score if enough time has passed
            time_since_update = datetime.utcnow() - profile.last_activity
            if time_since_update > timedelta(hours=1):
                profile.engagement_score = self._calculate_engagement_score(profile)
                profile.activity_level = self._determine_activity_level(profile.engagement_score)

    async def _check_campaign_triggers(self) -> None:
        """Check for and trigger engagement-based campaigns."""
        for group_id in set(p.group_id for p in self.engagement_profiles.values()):
            # Check if group needs re-engagement campaign
            inactive_count = len([
                p for p in self.engagement_profiles.values()
                if p.group_id == group_id and p.activity_level == "low"
            ])

            total_users = len([
                p for p in self.engagement_profiles.values()
                if p.group_id == group_id
            ])

            if total_users > 0 and (inactive_count / total_users) > 0.6:
                await self.trigger_engagement_campaign(group_id, "re_engagement")

    async def stop_worker(self) -> None:
        """Stop the engagement worker."""
        logger.info("Stopping EngagementWorker")
        self.is_running = False

    # Advanced Features Implementation

    async def trigger_onboarding_dm(self, user_id: str, group_id: str) -> None:
        """Trigger onboarding DM for new members."""
        onboarding_flow = self.onboarding_flows.get("default")
        if not onboarding_flow:
            return

        welcome_message = onboarding_flow.welcome_message

        try:
            await self.groupme.messages.post_to_group(
                group_id=group_id,
                source_guid=str(uuid.uuid4()),
                text=welcome_message
            )

            logger.info(f"Sent onboarding message to new user {user_id}")

        except Exception as e:
            logger.error(f"Failed to send onboarding message: {e}")

    async def check_gamification_progression(self, user_id: str, group_id: str) -> None:
        """Check if user should progress to next gamification level."""
        profile_key = f"{group_id}:{user_id}"
        profile = self.engagement_profiles.get(profile_key)

        if not profile:
            return

        current_level = self._get_current_gamification_level(profile.engagement_score)

        if current_level and current_level != profile.activity_level:
            await self._unlock_gamification_level(user_id, group_id, current_level)

    def _get_current_gamification_level(self, engagement_score: float) -> Optional[str]:
        """Get current gamification level based on engagement score."""
        levels = [
            ("bronze", 0.3), ("silver", 0.6), ("gold", 0.8), ("platinum", 0.9)
        ]

        for level, threshold in levels:
            if engagement_score >= threshold:
                return level

        return None

    async def _unlock_gamification_level(self, user_id: str, group_id: str, level: str) -> None:
        """Unlock gamification level for user."""
        level_messages = {
            "bronze": "Welcome to Bronze level!",
            "silver": "Congratulations on Silver!",
            "gold": "Amazing! You've reached Gold!",
            "platinum": "Incredible! Platinum status achieved!"
        }

        message = level_messages.get(level, f"Level up to {level}!")

        try:
            await self.groupme.messages.post_to_group(
                group_id=group_id,
                source_guid=str(uuid.uuid4()),
                text=message
            )

            logger.info(f"User {user_id} leveled up to {level}")

        except Exception as e:
            logger.error(f"Failed to send level up message: {e}")

    async def trigger_phantom_mention(self, group_id: str, criteria: Dict[str, Any]) -> None:
        """Trigger phantom mention campaign."""
        target_users = await self._get_mention_targets(group_id, criteria)

        if not target_users:
            return

        mention_list = ", ".join([f"@{user}" for user in target_users[:criteria.get("max_mentions", 50)]])

        message = criteria.get("message_template", "Hey everyone!").format(users=mention_list)

        try:
            await self.groupme.messages.post_to_group(
                group_id=group_id,
                source_guid=str(uuid.uuid4()),
                text=message
            )

            logger.info(f"Sent phantom mention to {len(target_users)} users")

        except Exception as e:
            logger.error(f"Failed to send phantom mention: {e}")

    async def _get_mention_targets(self, group_id: str, criteria: Dict[str, Any]) -> List[str]:
        """Get users to mention based on criteria."""
        targets = []

        for profile in self.engagement_profiles.values():
            if profile.group_id != group_id:
                continue

            if criteria.get("active_only") and profile.activity_level not in ["high", "very_high"]:
                continue

            if criteria.get("inactive_days"):
                days_inactive = (datetime.utcnow() - profile.last_activity).days
                if days_inactive < criteria["inactive_days"]:
                    continue

            targets.append(profile.user_id)

        return targets

    def set_shadow_mode(self, group_id: str, enabled: bool) -> None:
        """Enable or disable shadow mode for a group."""
        self.shadow_mode_active[group_id] = enabled

        if enabled:
            logger.info(f"Shadow mode enabled for group {group_id}")
        else:
            logger.info(f"Shadow mode disabled for group {group_id}")

    def add_context_trigger(self, group_id: str, trigger_keyword: str) -> None:
        """Add a context trigger for dynamic promotions."""
        if trigger_keyword not in self.context_triggers[group_id]:
            self.context_triggers[group_id].append(trigger_keyword)
            logger.info(f"Added context trigger '{trigger_keyword}' for group {group_id}")

    async def generate_dynamic_promotion(self, message_text: str, group_id: str) -> Optional[str]:
        """Generate dynamic context-triggered promotions."""
        message_lower = message_text.lower()

        for trigger in self.context_triggers.get(group_id, []):
            if trigger in message_lower:
                if trigger in ["shoes", "sneakers", "footwear"]:
                    return "Just saw a great deal on shoes - check it out: [affiliate_link]"
                elif trigger in ["tech", "gadget", "device"]:
                    return "Hot new tech gadget alert - perfect for what you're discussing! [affiliate_link]"

        return None
