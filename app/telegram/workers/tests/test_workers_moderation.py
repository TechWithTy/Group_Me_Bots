"""Tests for the moderation worker."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import asyncio

from ..workers.moderation import ModerationPlan, run_moderation_workflow


def test_run_moderation_workflow_warns_on_violation():
    groupme = SimpleNamespace(messages=SimpleNamespace(post_to_group=AsyncMock()))
    plan = ModerationPlan(
        group_id="group-1",
        user_id="user-42",
        message_text="This is blatant spam content",
    )

    asyncio.run(run_moderation_workflow(groupme, plan))

    assert groupme.messages.post_to_group.await_count == 1
    kwargs = groupme.messages.post_to_group.await_args.kwargs
    assert kwargs["group_id"] == "group-1"
    assert "warning" in kwargs["text"].lower()
    assert "user-42" in kwargs["text"]


def test_run_moderation_workflow_no_action_for_clean_message():
    groupme = SimpleNamespace(messages=SimpleNamespace(post_to_group=AsyncMock()))
    plan = ModerationPlan(group_id="group-1", user_id="user-42", message_text="Hope you are well!")

    asyncio.run(run_moderation_workflow(groupme, plan))

    groupme.messages.post_to_group.assert_not_awaited()
