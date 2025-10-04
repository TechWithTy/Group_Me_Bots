"""Advanced worker for orchestrating group migrations and growth tactics."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Sequence
from uuid import uuid4

from app.models import MemberAddRequest

logger = logging.getLogger(__name__)

MAX_MEMBERS_PER_BATCH = 10


@dataclass(slots=True)
class MigrationPlan:
    """Instructions for migrating engaged users into target groups."""

    source_group_id: str
    target_group_ids: Sequence[str]
    engaged_user_ids: set[str] | None = None
    exclude_user_ids: set[str] = field(default_factory=set)
    max_invites: int | None = None
    share_link_template: str | None = None
    post_migration_template: str | None = None


@dataclass(slots=True)
class MigrationReport:
    """Summary of migration actions performed."""

    invited_user_ids: dict[str, List[str]]
    share_links: dict[str, str]
    posted_messages: List[str]
    skipped_user_ids: List[str]


def _chunked(items: List[dict[str, str]], size: int) -> Iterable[List[dict[str, str]]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def _select_members(plan: MigrationPlan, members: Sequence[Any]) -> tuple[List[tuple[str, str]], List[str]]:
    selected: List[tuple[str, str]] = []
    skipped: List[str] = []
    for member in members:
        user_id = getattr(member, "user_id", None) or getattr(member, "id", None)
        if not user_id:
            continue
        if user_id in plan.exclude_user_ids:
            skipped.append(user_id)
            continue
        if plan.engaged_user_ids is not None and user_id not in plan.engaged_user_ids:
            skipped.append(user_id)
            continue
        nickname = getattr(member, "nickname", None) or "Member"
        selected.append((user_id, nickname))
    if plan.max_invites is not None and len(selected) > plan.max_invites:
        overflow = selected[plan.max_invites :]
        skipped.extend(user_id for user_id, _ in overflow)
        selected = selected[: plan.max_invites]
    return selected, skipped


async def run_migration_workflow(groupme: Any, plan: MigrationPlan) -> MigrationReport:
    """Execute a multi-target migration campaign following growth-hack guidance."""

    logger.info(
        "Starting migration for source group %s into %d targets",
        plan.source_group_id,
        len(plan.target_group_ids),
    )
    source_group = await groupme.groups.get(plan.source_group_id)
    members = getattr(source_group, "members", None) or []
    selected_members, skipped_members = _select_members(plan, members)

    if not selected_members:
        logger.info("No eligible members identified for migration.")

    invite_payload = [
        {"nickname": nickname, "user_id": user_id}
        for user_id, nickname in selected_members
    ]

    invited_per_target: dict[str, List[str]] = {}
    posted_messages: List[str] = []
    share_links: dict[str, str] = {}

    for target_group_id in plan.target_group_ids:
        if not invite_payload:
            invited_per_target[target_group_id] = []
            continue
        for batch in _chunked(invite_payload, MAX_MEMBERS_PER_BATCH):
            request = MemberAddRequest(members=batch)
            logger.debug(
                "Inviting %d members from %s to %s", len(batch), plan.source_group_id, target_group_id
            )
            await groupme.groups.add_members(target_group_id, request)
        invited_per_target[target_group_id] = [entry["user_id"] for entry in invite_payload]

        target_group = await groupme.groups.get(target_group_id)
        if plan.share_link_template and getattr(target_group, "share_url", None):
            message = plan.share_link_template.format(
                share_url=target_group.share_url,
                target_group_name=getattr(target_group, "name", target_group_id),
                source_group_name=getattr(source_group, "name", plan.source_group_id),
            )
            await groupme.messages.post_to_group(
                group_id=plan.source_group_id,
                source_guid=str(uuid4()),
                text=message,
            )
            posted_messages.append(message)
            share_links[target_group_id] = target_group.share_url

        if plan.post_migration_template:
            context = {
                "target_group_name": getattr(target_group, "name", target_group_id),
                "source_group_name": getattr(source_group, "name", plan.source_group_id),
                "share_url": getattr(target_group, "share_url", ""),
                "user_count": len(invited_per_target[target_group_id]),
            }
            message = plan.post_migration_template.format(**context)
            await groupme.messages.post_to_group(
                group_id=target_group_id,
                source_guid=str(uuid4()),
                text=message,
            )
            posted_messages.append(message)

    return MigrationReport(
        invited_user_ids=invited_per_target,
        share_links=share_links,
        posted_messages=posted_messages,
        skipped_user_ids=skipped_members,
    )