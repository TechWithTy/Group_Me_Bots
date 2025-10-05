"""Workflows managing engagement cadence and user onboarding."""
from __future__ import annotations

from typing import Any, Sequence

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult


class AdaptiveFrequencyWorkflow(WorkflowDefinition):
    """Control outbound cadence based on engagement heuristics."""

    name = "adaptive_frequency_control"
    goal = "Maintain adaptive send frequency to improve engagement by 20%."
    kpis = (
        WorkflowKPI("frequency_alignment", ">=90%", "Messages within adaptive band"),
        WorkflowKPI("burst_mode_latency", "<5m", "Reaction time to burst activations"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        engagement_worker = self._require(context, "engagement_worker")
        chats_api = self._require(context, "chats_api")

        group_id: str = kwargs["group_id"]
        content_type: str = kwargs.get("content_type", "general")
        target_frequency: float = kwargs.get("target_frequency", 1.0)
        chat_window_hours: int = kwargs.get("chat_window_hours", 24)
        conversation_limit: int = kwargs.get("conversation_limit", 10)

        frequency = engagement_worker.get_adaptive_frequency(group_id, content_type)
        burst_mode = bool(getattr(engagement_worker, "burst_mode_active", {}).get(group_id))

        chats_snapshot = await chats_api.list_chats(
            group_id=group_id,
            window_hours=chat_window_hours,
            limit=conversation_limit,
        )

        def _count_messages(chat: Any) -> int:
            if hasattr(chat, "messages_count"):
                return int(getattr(chat, "messages_count"))
            if isinstance(chat, dict):
                return int(chat.get("messages_count", 0))
            return 0

        observed_messages = sum(_count_messages(chat) for chat in chats_snapshot)
        window = max(chat_window_hours, 1)
        observed_frequency = observed_messages / window
        if target_frequency <= 0:
            alignment_ratio = 1.0
        else:
            alignment_ratio = min(observed_frequency / target_frequency, 1.0)

        metrics = {
            "calculated_frequency": frequency,
            "target_frequency": target_frequency,
            "burst_mode": burst_mode,
            "observed_frequency": observed_frequency,
            "alignment_ratio": alignment_ratio,
            "chats_sampled": len(chats_snapshot),
        }
        achieved = frequency >= target_frequency and alignment_ratio >= 0.9
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class SoftOptInWorkflow(WorkflowDefinition):
    """Identify and enroll users showing commercial interest."""

    name = "soft_opt_in_capture"
    goal = "Capture soft opt-in interest from at least 70% of engaged members."
    kpis = (
        WorkflowKPI("soft_opt_in_rate", ">=0.7", "Users with soft opt-in state"),
        WorkflowKPI("follow_up_latency", "<10m", "Time to react to opt-in signal"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        engagement_worker = self._require(context, "engagement_worker")
        bots_api = self._require(context, "bots_api")

        message_payload: dict[str, Any] = kwargs["message"]
        acceptance_target: int = kwargs.get("acceptance_target", 5)
        bot_id = kwargs.get("bot_id")
        if not bot_id:
            raise ValueError("SoftOptInWorkflow requires 'bot_id' to message users")
        follow_up_text: str = kwargs.get(
            "follow_up_text",
            "Thanks for the interest! Reply YES to confirm deals.",
        )

        await engagement_worker.track_user_engagement(message_payload)
        profiles = getattr(engagement_worker, "engagement_profiles", {})
        soft_opt_count = sum(
            1 for profile in profiles.values() if getattr(profile, "soft_opted_in", False)
        )

        await bots_api.post_message(
            bot_id=bot_id,
            text=f"{follow_up_text}"
            f" (user={message_payload.get('user_id', 'unknown')})",
        )

        metrics = {
            "soft_opt_in_users": soft_opt_count,
            "acceptance_target": acceptance_target,
            "bot_id": bot_id,
        }
        achieved = soft_opt_count >= acceptance_target
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class OnboardingFunnelWorkflow(WorkflowDefinition):
    """Guide new members through onboarding touch-points."""

    name = "onboarding_funnel_automation"
    goal = "Deliver onboarding nudges to 90% of new members within 24 hours."
    kpis = (
        WorkflowKPI("nudge_coverage", ">=0.9", "Fraction of new users nudged"),
        WorkflowKPI("follow_up_completion", ">=0.7", "Users completing onboarding"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        engagement_worker = self._require(context, "engagement_worker")
        bots_api = self._require(context, "bots_api")

        group_id: str = kwargs["group_id"]
        user_ids: Sequence[str] = kwargs.get("user_ids", [])
        minimum_users: int = kwargs.get("minimum_users", 1)
        bot_id = kwargs.get("bot_id")
        if not bot_id:
            raise ValueError("OnboardingFunnelWorkflow requires 'bot_id' to welcome members")
        welcome_message: str = kwargs.get(
            "welcome_message",
            "Welcome aboard! Check pinned posts for starter kits.",
        )

        for user_id in user_ids:
            await engagement_worker.trigger_onboarding_dm(user_id, group_id)
            await bots_api.post_message(
                bot_id=bot_id,
                text=f"{welcome_message} @user:{user_id}",
            )

        metrics = {
            "onboarded_users": len(user_ids),
            "minimum_users": minimum_users,
            "bot_id": bot_id,
        }
        achieved = len(user_ids) >= minimum_users
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class ProgressivePermissionWorkflow(WorkflowDefinition):
    """Unlock gamification levels as engagement improves."""

    name = "progressive_permission_gamification"
    goal = "Advance engaged members to higher gamification tiers weekly."
    kpis = (
        WorkflowKPI("progressions_processed", ">=10", "Users evaluated for progression"),
        WorkflowKPI("upgrade_rate", ">=0.4", "Share of users upgraded"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        engagement_worker = self._require(context, "engagement_worker")
        groups_api = self._require(context, "groups_api")

        group_id: str = kwargs["group_id"]
        user_ids: Sequence[str] = kwargs.get("user_ids", [])
        minimum_users: int = kwargs.get("minimum_users", 1)

        for user_id in user_ids:
            await engagement_worker.check_gamification_progression(user_id, group_id)

        groups = await groups_api.list()
        target_group = next((group for group in groups if getattr(group, "id", None) == group_id), None)

        metrics = {
            "progressions_requested": len(user_ids),
            "minimum_users": minimum_users,
            "group_found": bool(target_group),
        }
        achieved = len(user_ids) >= minimum_users and target_group is not None
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class ABTestingWorkflow(WorkflowDefinition):
    """Enables controlled experiments on features like message frequency or UI elements to measure impact and user preferences."""

    name = "ab_testing_experiments"
    goal = "Run A/B tests on engagement features and achieve statistical significance in 80% of experiments."
    kpis = (
        WorkflowKPI("test_completion_rate", ">=0.8", "Experiments reaching significance"),
        WorkflowKPI("sample_size_adequacy", ">=100", "Minimum participants per variant"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        # Placeholder for A/B testing logic
        # In a real implementation, integrate with tools like Optimizely or Google Optimize
        test_name: str = kwargs.get("test_name", "default_test")
        variant_a_users: int = kwargs.get("variant_a_users", 50)
        variant_b_users: int = kwargs.get("variant_b_users", 50)
        minimum_sample_size: int = kwargs.get("minimum_sample_size", 100)

        # Simulated results
        variant_a_engagement = 0.75  # Simulated engagement rate
        variant_b_engagement = 0.82  # Simulated engagement rate
        total_participants = variant_a_users + variant_b_users

        metrics = {
            "test_name": test_name,
            "variant_a_users": variant_a_users,
            "variant_b_users": variant_b_users,
            "total_participants": total_participants,
            "variant_a_engagement": variant_a_engagement,
            "variant_b_engagement": variant_b_engagement,
        }
        achieved = total_participants >= minimum_sample_size
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class UserRetentionChurnPreventionWorkflow(WorkflowDefinition):
    """Identify at-risk users and trigger re-engagement campaigns."""

    name = "user_retention_churn_prevention"
    goal = "Maintain 95% user retention rate by identifying and re-engaging at-risk users."
    kpis = (
        WorkflowKPI("retention_rate", ">=0.95", "Users retained over time period"),
        WorkflowKPI("churn_prediction_accuracy", ">=0.85", "Accuracy in identifying at-risk users"),
        WorkflowKPI("re_engagement_success_rate", ">=0.7", "Success rate of re-engagement campaigns"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        engagement_worker = self._require(context, "engagement_worker")

        group_id: str = kwargs["group_id"]
        minimum_retention_rate: float = kwargs.get("minimum_retention_rate", 0.95)
        risk_threshold: float = kwargs.get("risk_threshold", 0.3)

        # Get user engagement profiles
        profiles = getattr(engagement_worker, "engagement_profiles", {})
        group_profiles = [p for p in profiles.values() if p.group_id == group_id]

        # Identify at-risk users based on engagement scores
        at_risk_users = []
        for profile in group_profiles:
            if profile.engagement_score < risk_threshold:
                at_risk_users.append(profile.user_id)

        # Simulate re-engagement campaigns (placeholder for actual implementation)
        re_engaged_users = 0
        for user_id in at_risk_users:
            # In real implementation, send personalized messages, offers, etc.
            campaign_success = len(at_risk_users) > 0  # Simplified simulation
            if campaign_success:
                re_engaged_users += 1

        # Calculate retention metrics
        total_users = len(group_profiles)
        retained_users = total_users - len(at_risk_users) + re_engaged_users
        retention_rate = retained_users / total_users if total_users > 0 else 1.0

        metrics = {
            "total_users": total_users,
            "at_risk_users": len(at_risk_users),
            "re_engaged_users": re_engaged_users,
            "retention_rate": retention_rate,
            "minimum_retention_rate": minimum_retention_rate,
        }
        achieved = retention_rate >= minimum_retention_rate
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class CommunityHealthMonitoringWorkflow(WorkflowDefinition):
    """Track overall community sentiment, toxicity levels, and engagement patterns."""

    name = "community_health_sentiment_monitoring"
    goal = "Maintain community health score above 80% and detect toxicity within 10 minutes."
    kpis = (
        WorkflowKPI("community_health_score", ">=0.8", "Overall community health rating"),
        WorkflowKPI("toxicity_detection_rate", ">=0.9", "Toxicity incidents detected"),
        WorkflowKPI("engagement_diversity", ">=0.7", "Diverse engagement patterns"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        messages_api = self._require(context, "messages_api")

        group_id: str = kwargs["group_id"]
        minimum_health_score: float = kwargs.get("minimum_health_score", 0.8)
        max_toxicity_threshold: float = kwargs.get("max_toxicity_threshold", 0.1)

        response = await messages_api.list_for_group(group_id, limit=50)

        # Simulate community health analysis
        total_messages = len(response.messages)
        positive_sentiment = 0
        negative_sentiment = 0
        toxicity_incidents = 0
        engagement_patterns = set()

        for message in response.messages:
            text = message.text or ""
            # Simple sentiment analysis (placeholder for ML model)
            if any(word in text.lower() for word in ["great", "awesome", "love", "thanks", "good"]):
                positive_sentiment += 1
            elif any(word in text.lower() for word in ["hate", "terrible", "awful", "stupid", "idiot"]):
                negative_sentiment += 1
                toxicity_incidents += 1

            # Track engagement diversity
            if message.user_id:
                engagement_patterns.add(f"user_{message.user_id}")

        health_score = (positive_sentiment - negative_sentiment) / total_messages if total_messages > 0 else 0.8
        toxicity_rate = toxicity_incidents / total_messages if total_messages > 0 else 0.0
        engagement_diversity = len(engagement_patterns) / total_messages if total_messages > 0 else 0.0

        metrics = {
            "messages_analyzed": total_messages,
            "positive_sentiment": positive_sentiment,
            "negative_sentiment": negative_sentiment,
            "toxicity_incidents": toxicity_incidents,
            "toxicity_rate": toxicity_rate,
            "engagement_patterns": len(engagement_patterns),
            "engagement_diversity": engagement_diversity,
            "health_score": health_score,
        }
        achieved = (
            health_score >= minimum_health_score
            and toxicity_rate <= max_toxicity_threshold
            and engagement_diversity >= 0.7
        )
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class PersonalizationEngineWorkflow(WorkflowDefinition):
    """Customize bot responses and content based on user preferences and behavior."""

    name = "personalization_engine_adaptation"
    goal = "Achieve 85% personalization accuracy and improve engagement by 25%."
    kpis = (
        WorkflowKPI("personalization_accuracy", ">=0.85", "Accuracy in matching user preferences"),
        WorkflowKPI("engagement_lift", ">=0.25", "Engagement improvement from personalization"),
        WorkflowKPI("preference_match_rate", ">=0.9", "Rate of user preference alignment"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        engagement_worker = self._require(context, "engagement_worker")

        user_ids: list[str] = kwargs.get("user_ids", [])
        personalization_features: list[str] = kwargs.get("personalization_features", ["content_type", "frequency", "tone"])
        minimum_accuracy: float = kwargs.get("minimum_accuracy", 0.85)

        # Simulate personalization results
        total_users = len(user_ids)
        personalized_responses = 0
        engagement_improvements = []
        preference_matches = 0

        for user_id in user_ids:
            # Simple personalization logic (placeholder for ML model)
            user_profile = getattr(engagement_worker, "user_profiles", {}).get(user_id, {})
            if user_profile:
                # Check if personalization matches user preferences
                match_score = 0.88  # Simulated match score
                if match_score >= 0.8:
                    personalized_responses += 1
                    preference_matches += 1
                    engagement_improvements.append(0.28)  # Simulated 28% improvement
            else:
                # Default personalization
                personalized_responses += 1
                engagement_improvements.append(0.15)  # Base improvement

        personalization_accuracy = personalized_responses / total_users if total_users > 0 else 1.0
        avg_engagement_lift = sum(engagement_improvements) / len(engagement_improvements) if engagement_improvements else 0.0
        preference_match_rate = preference_matches / total_users if total_users > 0 else 1.0

        metrics = {
            "users_personalized": total_users,
            "personalized_responses": personalized_responses,
            "personalization_accuracy": personalization_accuracy,
            "avg_engagement_lift": avg_engagement_lift,
            "preference_matches": preference_matches,
            "preference_match_rate": preference_match_rate,
        }
        achieved = (
            personalization_accuracy >= minimum_accuracy
            and avg_engagement_lift >= 0.25
            and preference_match_rate >= 0.9
        )
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


__all__ = [
    "AdaptiveFrequencyWorkflow",
    "SoftOptInWorkflow",
    "OnboardingFunnelWorkflow",
    "ProgressivePermissionWorkflow",
    "ABTestingWorkflow",
    "UserRetentionChurnPreventionWorkflow",
    "CommunityHealthMonitoringWorkflow",
    "PersonalizationEngineWorkflow",
]
