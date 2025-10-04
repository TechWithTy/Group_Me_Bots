"""Tests for the advanced migration worker."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.models import Group, Member
from workers.migration import MigrationPlan, run_migration_workflow


def test_run_migration_workflow_invites_engaged_members():
    members = [
        Member(user_id="u-1", nickname="A"),
        Member(user_id="u-2", nickname="B"),
    ]
    source_group = Group(id="source", name="Source", members=members)
    target_group = Group(id="target", name="Target", share_url="https://example.com/invite")

    groups_api = SimpleNamespace(
        get=AsyncMock(side_effect=[source_group, target_group]),
        add_members=AsyncMock(return_value="result-1"),
    )
    messages_api = SimpleNamespace(post_to_group=AsyncMock())
    groupme = SimpleNamespace(groups=groups_api, messages=messages_api)

    plan = MigrationPlan(
        source_group_id="source",
        target_group_ids=("target",),
        engaged_user_ids={"u-1"},
        share_link_template="Join {target_group_name}: {share_url}",
    )

    report = asyncio.run(run_migration_workflow(groupme, plan))

    assert groups_api.add_members.await_count == 1
    payload = groups_api.add_members.await_args.args[1]
    assert payload.members == [{"nickname": "A", "user_id": "u-1"}]

    assert report.invited_user_ids == {"target": ["u-1"]}
    assert report.share_links == {"target": "https://example.com/invite"}
    messages_api.post_to_group.assert_awaited_once()
    posted_text = messages_api.post_to_group.await_args.kwargs["text"]
    assert "Join Target" in posted_text


def test_run_migration_workflow_respects_max_invites_and_skips():
    members = [
        Member(user_id="u-1", nickname="Alpha"),
        Member(user_id="u-2", nickname="Beta"),
        Member(user_id=None, nickname="Ghost"),
    ]
    source_group = Group(id="source", name="Source", members=members)
    target_group = Group(id="target", name="Target", share_url="https://example.com/invite")

    groups_api = SimpleNamespace(
        get=AsyncMock(side_effect=[source_group, target_group]),
        add_members=AsyncMock(return_value="result-2"),
    )
    messages_api = SimpleNamespace(post_to_group=AsyncMock())
    groupme = SimpleNamespace(groups=groups_api, messages=messages_api)

    plan = MigrationPlan(
        source_group_id="source",
        target_group_ids=["target"],
        max_invites=1,
        share_link_template=None,
    )

    report = asyncio.run(run_migration_workflow(groupme, plan))

    payload = groups_api.add_members.await_args.args[1]
    assert payload.members == [{"nickname": "Alpha", "user_id": "u-1"}]
    assert report.invited_user_ids == {"target": ["u-1"]}
    assert report.skipped_user_ids == ["u-2"]
    messages_api.post_to_group.assert_not_awaited()


def test_run_migration_workflow_skips_share_without_url():
    members = [Member(user_id="u-1", nickname="A")]
    source_group = Group(id="source", name="Source", members=members)
    target_group = Group(id="target", name="Target", share_url=None)

    groups_api = SimpleNamespace(
        get=AsyncMock(side_effect=[source_group, target_group]),
        add_members=AsyncMock(return_value="result-3"),
    )
    messages_api = SimpleNamespace(post_to_group=AsyncMock())
    groupme = SimpleNamespace(groups=groups_api, messages=messages_api)

    plan = MigrationPlan(
        source_group_id="source",
        target_group_ids=["target"],
        share_link_template="Upgrade here: {share_url}",
    )

    report = asyncio.run(run_migration_workflow(groupme, plan))

    assert report.share_links == {}
    messages_api.post_to_group.assert_not_awaited()