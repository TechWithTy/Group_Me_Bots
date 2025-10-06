"""Worker for detecting intent from messages."""
from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

KEYWORD_INTENTS: dict[str, tuple[str, ...]] = {
    "commerce": ("buy", "purchase", "order", "catalog"),
    "moderation": ("spam", "report", "abuse", "ban"),
    "command": ("/", "!"),
}


@dataclass(slots=True)
class IntentPlan:
    """Plan for detecting intent from a message."""

    message_text: str


@dataclass(slots=True)
class IntentReport:
    """Report containing the detected intent."""

    intent: str
    confidence: float


def _classify_intent(message_text: str) -> IntentReport:
    lowered = message_text.lower()
    for intent, keywords in KEYWORD_INTENTS.items():
        if any(keyword in lowered for keyword in keywords):
            logger.debug("Detected intent '%s' for message: %s", intent, message_text)
            return IntentReport(intent=intent, confidence=0.9)
    logger.debug("Defaulting to chitchat intent for message: %s", message_text)
    return IntentReport(intent="chitchat", confidence=0.4)


async def run_intent_detection_workflow(plan: IntentPlan) -> IntentReport:
    """Analyze a message and return a detected intent."""
    logger.info("Detecting intent for incoming message")
    if not plan.message_text.strip():
        logger.debug("Empty message detected; returning low-confidence chitchat.")
        return IntentReport(intent="chitchat", confidence=0.1)
    return _classify_intent(plan.message_text)
