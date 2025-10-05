"""Focused unit tests for worker utilities powering engagement workflows."""
from __future__ import annotations

import types
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("pydantic")

from workers.content_echo_worker import ContentEchoWorker, EchoRule
from workers.engagement_worker import EngagementWorker
from workers.tracking_worker import TrackingWorker
from workers.intent_detector import IntentPlan, run_intent_detection_workflow
from _schema.tracking import BrowserAction


@pytest.mark.asyncio
async def test_content_echo_worker_process_message_creates_echo_history():
    """Messages matching rules should be echoed across groups."""
    groupme_stub = types.SimpleNamespace(
        messages=types.SimpleNamespace(
            post_to_group=AsyncMock(return_value={"message": {"id": "echo-1"}})
        )
    )
    worker = ContentEchoWorker(groupme_stub, MagicMock())
    worker.echo_rules["g1"] = EchoRule(
        source_group_id="g1",
        target_group_ids=["g2"],
        engagement_threshold=1,
        echo_probability=1.0,
    )
    worker._get_message_engagement = AsyncMock(return_value=5)
    worker._should_echo_content = AsyncMock(return_value=True)

    message_data = {
        "id": "m1",
        "group_id": "g1",
        "text": "Limited deal available now!",
        "user_id": "u1",
        "name": "Alice",
    }

    await worker.process_message_for_echo(message_data)

    assert len(worker.echo_history) == 1
    event = worker.echo_history[0]
    assert event.target_group_id == "g2"
    assert event.original_message_id == "m1"


@pytest.mark.asyncio
async def test_engagement_worker_tracks_user_activity_and_soft_opt_in():
    """Engagement worker should create profiles while monitoring soft opt-ins."""
    groupme_stub = types.SimpleNamespace(messages=types.SimpleNamespace(post_to_group=AsyncMock()))
    worker = EngagementWorker(groupme_stub, MagicMock())
    worker._check_soft_opt_in_signals = AsyncMock()
    worker._update_group_engagement_metrics = AsyncMock()

    await worker.track_user_engagement(
        {
            "user_id": "user-1",
            "group_id": "group-1",
            "tenant_id": "tenant-1",
            "text": "I want to buy now",
        }
    )

    profile_key = "tenant-1:group-1:user-1"
    assert profile_key in worker.engagement_profiles
    assert worker.engagement_profiles[profile_key].message_count == 1
    worker._check_soft_opt_in_signals.assert_awaited()


@pytest.mark.asyncio
async def test_tracking_worker_browser_interaction_records_metrics():
    """Tracking worker should store browser interactions for analytics."""
    worker = TrackingWorker(types.SimpleNamespace(tenant_id="tenant-1"), MagicMock())
    worker.browser_config = types.SimpleNamespace(browser_type="chromium")

    interaction_id = await worker.track_browser_interaction(
        url="https://example.com",
        action=BrowserAction.NAVIGATE,
        parameters={"latency_budget_ms": 200},
        result={"status": "ok"},
    )

    assert any(interaction.id == interaction_id for interaction in worker.browser_interactions)


@pytest.mark.asyncio
async def test_intent_detector_reports_commerce_intent():
    """Intent detector should flag commerce-focused phrases with high confidence."""
    plan = IntentPlan(message_text="Can I buy this product today?")
    report = await run_intent_detection_workflow(plan)
    assert report.intent == "commerce"
    assert report.confidence >= 0.8
