"""Worker for processing custom commands."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Mapping
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CommandPlan:
    """Plan for processing a potential command."""

    group_id: str
    message_text: str
    command_store: Mapping[str, str] = field(default_factory=dict)
    prefix: str = "/"


async def run_command_workflow(groupme: Any, plan: CommandPlan) -> None:
    """Execute the custom command workflow."""
    logger.info("Checking for commands in group %s", plan.group_id)
    message = plan.message_text.strip()
    if not message or not message.startswith(plan.prefix):
        logger.debug("Message does not start with prefix '%s'; ignoring.", plan.prefix)
        return

    trigger = message.split(maxsplit=1)[0].lower()
    logger.debug("Extracted trigger '%s'", trigger)

    normalized_store = {key.lower(): value for key, value in plan.command_store.items()}
    response = normalized_store.get(trigger)
    if response is None:
        logger.debug("No stored command found for trigger '%s'", trigger)
        return

    logger.info("Found custom command for trigger '%s'; posting response.", trigger)
    await groupme.messages.post_to_group(
        group_id=plan.group_id,
        source_guid=str(uuid4()),
        text=response,
    )
