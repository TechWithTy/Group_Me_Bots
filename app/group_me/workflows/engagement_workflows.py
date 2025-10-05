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


__all__ = [
    "AdaptiveFrequencyWorkflow",
    "SoftOptInWorkflow",
    "OnboardingFunnelWorkflow",
    "ProgressivePermissionWorkflow",
]
