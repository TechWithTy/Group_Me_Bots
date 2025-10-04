"""Tests for the commerce worker."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import asyncio

from ..workers.commerce import CommercePlan, run_commerce_workflow


def test_run_commerce_workflow_sends_catalog():
    groupme = SimpleNamespace(messages=SimpleNamespace(post_to_group=AsyncMock()))
    plan = CommercePlan(group_id="group-9", user_id="user-9", message_text="@gort show me the catalog")

    report = asyncio.run(run_commerce_workflow(groupme, plan))

    groupme.messages.post_to_group.assert_awaited()
    kwargs = groupme.messages.post_to_group.await_args.kwargs
    assert kwargs["group_id"] == "group-9"
    assert "catalog" in kwargs["text"].lower()
    assert report.action == "catalog_sent"


def test_run_commerce_workflow_confirms_purchase():
    groupme = SimpleNamespace(messages=SimpleNamespace(post_to_group=AsyncMock()))
    plan = CommercePlan(group_id="group-9", user_id="user-9", message_text="@gort buy sunglasses")

    report = asyncio.run(run_commerce_workflow(groupme, plan))

    groupme.messages.post_to_group.assert_awaited()
    kwargs = groupme.messages.post_to_group.await_args.kwargs
    assert "confirmed" in kwargs["text"].lower()
    assert report.action == "order_confirmed"
