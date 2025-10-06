"""Regression tests for core Signal workflows."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

import pytest

from app.signal.workflows.base import WorkflowContext
from app.signal.workflows.engagement_workflows import (
    SignalAutoLikeFeedbackWorkflow,
    SignalContentQualityWorkflow,
    SignalEmergencyResponseWorkflow,
)
from app.signal.workflows.message_workflows import (
    SignalContentEchoWorkflow,
    SignalMessageStitchingWorkflow,
    SignalSecurityModerationWorkflow,
)
from tests.signal_workflow_stubs import (
    StubIntegrationsClient,
    StubPaymentsClient,
    StubSignalClient,
    StubStorageClient,
    StubTrackingWorker,
)


@pytest.fixture()
def workflow_context() -> WorkflowContext:
    messages = [
        {"id": "m1", "group_id": "g1", "text": "Great launch update", "reactions": 4},
        {"id": "m2", "group_id": "g1", "text": "Need urgent help", "reactions": 1},
        {
            "id": "m3",
            "group_id": "g1",
            "text": "Sharing secure document",
            "attachments": [{"type": "document"}],
            "reactions": 2,
        },
        {
            "id": "m4",
            "group_id": "g1",
            "text": "General conversation",
            "thread_id": "t2",
            "reactions": 0,
        },
        {
            "id": "m5",
            "group_id": "g1",
            "text": "Awesome photos",
            "attachments": [{"type": "image"}],
            "thread_id": "t2",
            "reactions": 5,
        },
    ]
    return WorkflowContext(
        signal_client=StubSignalClient(messages),
        storage_client=StubStorageClient(),
        integrations_client=StubIntegrationsClient(),
        payments_client=StubPaymentsClient(),
        tracking_worker=StubTrackingWorker(),
    )


@pytest.mark.asyncio()
async def test_auto_like_feedback_workflow_reacts_and_sends_receipts(workflow_context: WorkflowContext) -> None:
    workflow = SignalAutoLikeFeedbackWorkflow()

    result = await workflow.execute(
        workflow_context,
        group_id="g1",
        message_ids=["m1", "m2", "m3"],
        reaction_emoji="❤️",
    )

    assert result.achieved_goal is True
    assert result.metrics["reactions_sent"] == 3
    assert result.metrics["read_receipts_sent"] == 3
    assert any(action[0] == "group_message" for action in workflow_context.signal_client.actions)


@pytest.mark.asyncio()
async def test_content_quality_workflow_pins_high_quality_messages(workflow_context: WorkflowContext) -> None:
    workflow = SignalContentQualityWorkflow()

    result = await workflow.execute(workflow_context, group_id="g1", limit=10, highlight_limit=2)

    assert result.achieved_goal is True
    pinned = [payload for action, payload in workflow_context.signal_client.actions if action == "pin"]
    assert len(pinned) >= 1
    assert result.metrics["highlighted_messages"] == len(pinned)


@pytest.mark.asyncio()
async def test_emergency_response_workflow_escalates(workflow_context: WorkflowContext) -> None:
    workflow = SignalEmergencyResponseWorkflow()

    result = await workflow.execute(
        workflow_context,
        group_id="g1",
        emergency_keywords=("urgent",),
        escalation_contact="safety@signal.test",
    )

    assert result.achieved_goal is True
    forwards = [payload for action, payload in workflow_context.signal_client.actions if action == "forward"]
    assert forwards and forwards[0]["contact"] == "safety@signal.test"


@pytest.mark.asyncio()
async def test_message_stitching_workflow_builds_summaries(workflow_context: WorkflowContext) -> None:
    workflow = SignalMessageStitchingWorkflow()

    result = await workflow.execute(
        workflow_context,
        source_group="g1",
        target_groups=["g2", "g3"],
        limit=10,
    )

    assert result.achieved_goal is True
    group_messages = [action for action in workflow_context.signal_client.actions if action[0] == "group_message"]
    assert group_messages


@pytest.mark.asyncio()
async def test_security_moderation_workflow_reports_sensitive_content(workflow_context: WorkflowContext) -> None:
    workflow = SignalSecurityModerationWorkflow()

    result = await workflow.execute(workflow_context, group_id="g1", limit=10)

    assert result.achieved_goal is True
    reports = [payload for action, payload in workflow_context.signal_client.actions if action == "report"]
    assert reports and reports[0]["message"]["id"] == "m3"


@pytest.mark.asyncio()
async def test_content_echo_workflow_delivers_to_multiple_targets(workflow_context: WorkflowContext) -> None:
    workflow = SignalContentEchoWorkflow()

    result = await workflow.execute(
        workflow_context,
        source_group="g1",
        target_groups=["g2"],
        vip_contacts=["vip@signal.test"],
        story_enabled=True,
    )

    assert result.achieved_goal is True
    deliveries = [
        action
        for action in workflow_context.signal_client.actions
        if action[0] in {"group_message", "forward"}
    ]
    assert len(deliveries) >= 2
    stories = [action for action in workflow_context.signal_client.actions if action[0] == "story"]
    assert stories
