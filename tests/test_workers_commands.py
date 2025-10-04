"""Tests for the custom command worker."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import asyncio

from ..workers.commands import CommandPlan, run_command_workflow


def test_run_command_workflow_posts_known_command():
    command_store = {"/weather": "Expect sunshine all day."}
    groupme = SimpleNamespace(messages=SimpleNamespace(post_to_group=AsyncMock()))
    plan = CommandPlan(group_id="group-7", message_text="/weather", command_store=command_store)

    asyncio.run(run_command_workflow(groupme, plan))

    groupme.messages.post_to_group.assert_awaited()
    kwargs = groupme.messages.post_to_group.await_args.kwargs
    assert kwargs["group_id"] == "group-7"
    assert "sunshine" in kwargs["text"].lower()


def test_run_command_workflow_ignores_unknown_command():
    command_store = {"/weather": "Expect sunshine all day."}
    groupme = SimpleNamespace(messages=SimpleNamespace(post_to_group=AsyncMock()))
    plan = CommandPlan(group_id="group-7", message_text="/unknown", command_store=command_store)

    asyncio.run(run_command_workflow(groupme, plan))

    groupme.messages.post_to_group.assert_not_awaited()
