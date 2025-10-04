"""CLI entry point for GroupMe workflows."""
from __future__ import annotations

import asyncio
import os
from typing import Mapping

from app import GroupMe, bots
from workers import (
    CommandPlan,
    CommercePlan,
    IntentPlan,
    ModerationPlan,
    run_command_workflow,
    run_commerce_workflow,
    run_intent_detection_workflow,
    run_moderation_workflow,
    run_posting_workflow,
)


async def dispatch_message(
    groupme: GroupMe,
    *,
    group_id: str,
    user_id: str,
    message_text: str,
    command_store: Mapping[str, str] | None = None,
) -> None:
    """Route an incoming message through intent detection and downstream workers."""
    intent_report = await run_intent_detection_workflow(IntentPlan(message_text=message_text))

    if intent_report.intent == "commerce":
        await run_commerce_workflow(
            groupme,
            CommercePlan(group_id=group_id, user_id=user_id, message_text=message_text),
        )
    elif intent_report.intent == "moderation":
        await run_moderation_workflow(
            groupme,
            ModerationPlan(group_id=group_id, user_id=user_id, message_text=message_text),
        )
    elif intent_report.intent == "command":
        await run_command_workflow(
            groupme,
            CommandPlan(
                group_id=group_id,
                message_text=message_text,
                command_store=command_store or {},
            ),
        )


def _build_groupme_client() -> GroupMe:
    """Construct a GroupMe API client using environment configuration."""
    token = os.environ.get("GROUPME_TOKEN", "")
    if not token:
        raise RuntimeError("GROUPME_TOKEN environment variable must be set.")
    return GroupMe(token)


async def _run_webhook_loop() -> None:
    """Placeholder for webhook-driven processing that dispatches incoming messages."""
    groupme = _build_groupme_client()
    try:
        # TODO: Replace with webhook listener integration.
        await dispatch_message(
            groupme,
            group_id="demo-group",
            user_id="demo-user",
            message_text="/help",
            command_store={"/help": "Available commands: /help, /catalog"},
        )
    finally:
        await groupme.close()


def main() -> None:
    """Load bots and start the posting workflow."""
    bot_inventory = bots.get_bots()
    filtered_bots = bots.filter_bots(bot_inventory)
    run_posting_workflow(filtered_bots)


if __name__ == "__main__":
    main()
    # asyncio.run(_run_webhook_loop())
