"""Worker for handling commerce flows."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

MOCK_PRODUCT = {
    "name": "GORT Smart Shades",
    "description": "Adaptive tint sunglasses with voice assistant integration.",
    "price": "$199",
}


@dataclass(slots=True)
class CommercePlan:
    """Plan for a commerce-related action."""

    group_id: str
    user_id: str
    message_text: str


@dataclass(slots=True)
class CommerceReport:
    """Report describing the outcome of the commerce workflow."""

    action: str
    message: Optional[str]


def _build_catalog_message() -> str:
    """Create a mock catalog message for prototype flows."""
    return (
        "Today's catalog:\n"
        f"• {MOCK_PRODUCT['name']} — {MOCK_PRODUCT['price']}\n"
        f"  {MOCK_PRODUCT['description']}"
    )


def _build_confirmation_message(user_id: str) -> str:
    """Create a mock order confirmation message."""
    return (
        f"Order confirmed for {user_id}! {MOCK_PRODUCT['name']} is on its way. "
        "You'll receive ACP updates shortly."
    )


async def run_commerce_workflow(groupme: Any, plan: CommercePlan) -> CommerceReport:
    """Execute a commerce workflow based on user intent."""
    logger.info("Handling commerce intent for user %s", plan.user_id)
    message = plan.message_text.lower()

    if "catalog" in message:
        catalog_message = _build_catalog_message()
        logger.debug("Sending catalog to group %s", plan.group_id)
        await groupme.messages.post_to_group(
            group_id=plan.group_id,
            source_guid=str(uuid4()),
            text=catalog_message,
        )
        return CommerceReport(action="catalog_sent", message=catalog_message)

    if "buy" in message or "purchase" in message:
        confirmation = _build_confirmation_message(plan.user_id)
        logger.debug("Confirming order for user %s", plan.user_id)
        await groupme.messages.post_to_group(
            group_id=plan.group_id,
            source_guid=str(uuid4()),
            text=confirmation,
        )
        return CommerceReport(action="order_confirmed", message=confirmation)

    logger.debug("No commerce action detected for message: %s", plan.message_text)
    return CommerceReport(action="no_action", message=None)
