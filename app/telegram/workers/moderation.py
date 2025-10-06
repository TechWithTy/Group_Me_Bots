"""Worker for handling message moderation."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

VIOLATION_KEYWORDS: tuple[str, ...] = (
    "spam",
    "scam",
    "offensive",
    "abuse",
)


@dataclass(slots=True)
class ModerationPlan:
    """Plan for processing a single message for moderation."""

    group_id: str
    user_id: str
    message_text: str


@dataclass(slots=True)
class ModerationReport:
    """Summary of actions taken during moderation."""

    action: Optional[str]
    severity: float
    notes: Optional[str] = None


def _detect_violation(message_text: str, keywords: Iterable[str]) -> bool:
    """Return True when the message contains one of the violation keywords."""
    lowered = message_text.lower()
    return any(keyword in lowered for keyword in keywords)


async def run_moderation_workflow(groupme: Any, plan: ModerationPlan) -> ModerationReport:
    """Execute the moderation workflow for a given message."""
    logger.info("Moderating message from user %s in group %s", plan.user_id, plan.group_id)

    if not plan.message_text.strip():
        logger.debug("Empty message received; nothing to moderate.")
        return ModerationReport(action=None, severity=0.0, notes="empty-message")

    if not _detect_violation(plan.message_text, VIOLATION_KEYWORDS):
        logger.debug("Message deemed safe; no action taken.")
        return ModerationReport(action=None, severity=0.0)

    warning_text = (
        f"Moderation warning for {plan.user_id}: your recent message was flagged for review. "
        "Please adhere to community guidelines."
    )

    logger.warning(
        "Violation detected for user %s in group %s. Dispatching warning message.",
        plan.user_id,
        plan.group_id,
    )

    await groupme.messages.post_to_group(
        group_id=plan.group_id,
        source_guid=str(uuid4()),
        text=warning_text,
    )
    return ModerationReport(action="warn", severity=0.8, notes="keyword-violation")
