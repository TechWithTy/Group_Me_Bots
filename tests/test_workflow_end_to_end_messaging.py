"""End-to-end style tests for messaging and tracking workflows."""
from __future__ import annotations

import asyncio
import types
from typing import Any
from unittest.mock import AsyncMock

import pytest

from workflows.base import WorkflowContext
from workflows.growth_workflows import GhostInvitationWorkflow
from workflows.message_workflows import AutoLikeFeedbackWorkflow, MessageStitchingWorkflow
from workflows.tracking_workflows import ContentMiningWorkflow, RealTimeSubscriptionWorkflow


def test_message_stitching_workflow_executes_cross_group_echoes():
    """Workflow should stitch qualifying messages through the echo worker."""
    messages_api = types.SimpleNamespace(
        list_for_group=AsyncMock(
            return_value=types.SimpleNamespace(
                count=2,
                messages=[
                    types.SimpleNamespace(
                        id="m1",
                        source_guid="g1-1",
                        created_at=1,
                        user_id="u1",
                        group_id="g1",
                        name="User 1",
                        text="Flash sale today",
                    ),
                    types.SimpleNamespace(
                        id="m2",
                        source_guid="g1-2",
                        created_at=2,
                        user_id="u2",
                        group_id="g1",
                        name="User 2",
                        text="Limited offer",
                    ),
                ],
            )
        )
    )
    content_worker = types.SimpleNamespace(
        process_message_for_echo=AsyncMock(),
        echo_history=[],
    )

    async def _side_effect(message_data: dict[str, Any]) -> None:
        content_worker.echo_history.append({"id": message_data["id"]})

    content_worker.process_message_for_echo.side_effect = _side_effect

    context = WorkflowContext(messages_api=messages_api, content_echo_worker=content_worker)
    workflow = MessageStitchingWorkflow()
    result = asyncio.run(
        workflow.execute(
            context,
            group_id="g1",
            limit=10,
            target_echoes=2,
        )
    )

    assert result.achieved_goal is True
    assert result.metrics["processed_messages"] == 2
    assert result.metrics["echoed_messages"] == 2


def test_auto_like_feedback_workflow_posts_reactions():
    """Auto-like workflow should forward reactions to the messages API."""
    messages_api = types.SimpleNamespace(post_to_group=AsyncMock())
    context = WorkflowContext(messages_api=messages_api)
    workflow = AutoLikeFeedbackWorkflow()

    result = asyncio.run(
        workflow.execute(
            context,
            group_id="g42",
            message_ids=["m1", "m2"],
            reaction_text="👍",
        )
    )

    assert result.metrics["processed_messages"] == 2
    assert messages_api.post_to_group.await_count == 2
    assert result.achieved_goal is True


def test_real_time_subscription_workflow_tracks_events():
    """Real-time workflow should send captured events to tracking worker."""
    messages_api = types.SimpleNamespace(
        list_for_group=AsyncMock(
            return_value=types.SimpleNamespace(
                count=1,
                messages=[
                    types.SimpleNamespace(
                        id="m3",
                        source_guid="g1-3",
                        created_at=3,
                        user_id="u3",
                        group_id="g9",
                        name="User 3",
                        text="Engagement spike",
                    )
                ],
            )
        )
    )
    tracking_worker = types.SimpleNamespace(
        track_browser_interaction=AsyncMock(return_value="event-1"),
        browser_interactions=[],
    )

    async def _track(url: str, action: Any, parameters: dict[str, Any], result: dict[str, Any] | None = None):
        tracking_worker.browser_interactions.append({"url": url, "parameters": parameters})
        return "event-1"

    tracking_worker.track_browser_interaction.side_effect = _track

    context = WorkflowContext(messages_api=messages_api, tracking_worker=tracking_worker)
    workflow = RealTimeSubscriptionWorkflow()
    result = asyncio.run(workflow.execute(context, group_id="g9", limit=5))

    assert result.metrics["captured_events"] == 1
    assert tracking_worker.browser_interactions


def test_ghost_invitation_workflow_generates_links():
    """Ghost invitation workflow should return shareable invite links."""
    groups_api = types.SimpleNamespace(
        list=AsyncMock(
            return_value=[
                types.SimpleNamespace(id="g1", name="Alpha", share_url="https://group/alpha"),
                types.SimpleNamespace(id="g2", name="Beta", share_url=None),
            ]
        )
    )
    context = WorkflowContext(groups_api=groups_api)
    workflow = GhostInvitationWorkflow()
    result = asyncio.run(
        workflow.execute(context, target_groups=["g1", "g2"], minimum_links=1)
    )

    assert result.achieved_goal is True
    assert result.metrics["generated_links"] == ["https://group/alpha"]


def test_content_mining_workflow_combines_sources():
    """Content mining workflow should merge echo and tracking analytics."""
    content_worker = types.SimpleNamespace(
        run_content_mining=AsyncMock(return_value={"trending_topics": ["deal"]})
    )
    tracking_worker = types.SimpleNamespace(
        get_comprehensive_analytics=AsyncMock(return_value={"knowledge_base": []})
    )
    context = WorkflowContext(
        content_echo_worker=content_worker,
        tracking_worker=tracking_worker,
    )
    workflow = ContentMiningWorkflow()
    result = asyncio.run(workflow.execute(context, minimum_topics=1))

    assert result.metrics["trending_topics"] == ["deal"]
    assert result.metrics["analytics_snapshot"] == {"knowledge_base": []}
    assert result.achieved_goal is True
