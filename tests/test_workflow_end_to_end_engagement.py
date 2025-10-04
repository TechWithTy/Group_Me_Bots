"""End-to-end style tests for engagement and commerce workflows."""
from __future__ import annotations

import asyncio
import types
from unittest.mock import AsyncMock, MagicMock

import pytest

from workflows.base import WorkflowContext
from workflows.commerce_workflows import CommerceIntentWorkflow
from workflows.engagement_workflows import (
    AdaptiveFrequencyWorkflow,
    OnboardingFunnelWorkflow,
    ProgressivePermissionWorkflow,
    SoftOptInWorkflow,
)


def test_adaptive_frequency_workflow_uses_engagement_worker():
    """Adaptive frequency workflow should leverage engagement worker calculations."""
    engagement_worker = types.SimpleNamespace(
        get_adaptive_frequency=MagicMock(return_value=3.5),
        burst_mode_active={"group-1": True},
    )
    chats_api = types.SimpleNamespace(
        list_chats=AsyncMock(
            return_value=[types.SimpleNamespace(messages_count=90)]
        )
    )
    context = WorkflowContext(engagement_worker=engagement_worker, chats_api=chats_api)
    workflow = AdaptiveFrequencyWorkflow()

    result = asyncio.run(
        workflow.execute(
            context,
            group_id="group-1",
            content_type="promo",
            target_frequency=2.0,
        )
    )

    assert result.achieved_goal is True
    assert result.metrics["calculated_frequency"] == 3.5
    engagement_worker.get_adaptive_frequency.assert_called_once_with("group-1", "promo")
    chats_api.list_chats.assert_awaited()


def test_soft_opt_in_workflow_updates_profile_counts():
    """Soft opt-in workflow should tally users flagged for opt-ins."""
    profile = types.SimpleNamespace(soft_opted_in=True)
    engagement_worker = types.SimpleNamespace(
        engagement_profiles={"tenant:group:user": profile},
        track_user_engagement=AsyncMock(),
    )
    bots_api = types.SimpleNamespace(post_message=AsyncMock())
    context = WorkflowContext(engagement_worker=engagement_worker, bots_api=bots_api)
    workflow = SoftOptInWorkflow()

    result = asyncio.run(
        workflow.execute(
            context,
            message={
                "tenant_id": "tenant",
                "group_id": "group",
                "user_id": "user",
                "text": "buy now",
            },
            acceptance_target=1,
            bot_id="bot-1",
        )
    )

    assert result.achieved_goal is True
    assert result.metrics["soft_opt_in_users"] == 1
    engagement_worker.track_user_engagement.assert_awaited()
    bots_api.post_message.assert_awaited_once()


def test_commerce_intent_workflow_scores_messages():
    """Intent workflow should compute precision-like metrics for commerce intents."""
    messages_api = types.SimpleNamespace(
        list_for_group=AsyncMock(
            return_value=types.SimpleNamespace(
                messages=[types.SimpleNamespace(text="Fetched commerce offer")]
            )
        )
    )
    context = WorkflowContext(messages_api=messages_api)
    workflow = CommerceIntentWorkflow()

    result = asyncio.run(
        workflow.execute(
            context,
                messages=["Can I buy this?", "Ready to purchase now"],
                group_id="group-7",
                precision_target=0.3,
        )
    )

    assert result.metrics["commerce_intents"] >= 1
    assert result.achieved_goal is True
    messages_api.list_for_group.assert_awaited_once()


def test_onboarding_funnel_workflow_triggers_outreach():
    """Onboarding workflow should trigger direct messages for new users."""
    engagement_worker = types.SimpleNamespace(
        trigger_onboarding_dm=AsyncMock(),
    )
    bots_api = types.SimpleNamespace(post_message=AsyncMock())
    context = WorkflowContext(engagement_worker=engagement_worker, bots_api=bots_api)
    workflow = OnboardingFunnelWorkflow()

    result = asyncio.run(
        workflow.execute(
            context,
            group_id="group-x",
            user_ids=["u1", "u2"],
            bot_id="bot-42",
        )
    )

    assert engagement_worker.trigger_onboarding_dm.await_count == 2
    assert result.metrics["onboarded_users"] == 2
    assert result.achieved_goal is True
    assert bots_api.post_message.await_count == 2


def test_progressive_permission_workflow_checks_gamification():
    """Progressive permission workflow should request gamification updates."""
    engagement_worker = types.SimpleNamespace(
        check_gamification_progression=AsyncMock(),
    )
    groups_api = types.SimpleNamespace(
        list=AsyncMock(return_value=[types.SimpleNamespace(id="group-x")])
    )
    context = WorkflowContext(engagement_worker=engagement_worker, groups_api=groups_api)
    workflow = ProgressivePermissionWorkflow()

    result = asyncio.run(
        workflow.execute(
            context,
            group_id="group-x",
            user_ids=["user-1"],
            minimum_users=1,
        )
    )

    engagement_worker.check_gamification_progression.assert_awaited_once()
    groups_api.list.assert_awaited_once()
    assert result.metrics["progressions_requested"] == 1
    assert result.achieved_goal is True
