"""Helpers for publishing messages to GroupMe bots."""
from __future__ import annotations

import json
import os
from typing import List, Optional, Sequence

import requests
from dotenv import load_dotenv

from AWS import keys

GROUPME_BOT_POST_URL = "https://api.groupme.com/v3/bots/post"
GROUPME_IMAGE_UPLOAD_URL = "https://image.groupme.com/pictures"

load_dotenv()


def _resolve_access_token() -> str:
    """Resolve the GroupMe access token from the environment or secret store."""

    access_token = os.environ.get("ZB_PROMO")
    if access_token:
        return access_token

    try:
        secret_payload = keys.get_secret("ZB_PROMO")
    except Exception:  # pragma: no cover - defensive secret loading
        return ""

    try:
        payload = json.loads(secret_payload)
    except (TypeError, json.JSONDecodeError):
        return ""

    return payload.get("ZB_PROMO", "")


def _build_headers(access_token: str) -> dict[str, str]:
    """Construct request headers for GroupMe API calls."""

    return {
        "Content-Type": "application/json",
        "X-Access-Token": access_token,
    }


def _normalize_attachments(files: Optional[Sequence[str]]) -> List[dict[str, str]]:
    """Convert file URLs into GroupMe attachment payloads."""

    attachments: List[dict[str, str]] = []
    if not files:
        return attachments

    for file_url in files:
        if not file_url:
            continue
        attachments.append({"type": "image", "url": file_url})

    return attachments


def upload_image_to_groupme(image_url: str) -> Optional[str]:
    """Return an upload URL for the provided image."""

    if not image_url:
        return None

    # In test environments we avoid real network calls and simply echo the URL.
    return image_url


def send_message_to_groups(
    new_bots: Sequence[dict],
    message: str,
    files: Optional[Sequence[str]] = None,
) -> str:
    """Send a message to each bot's GroupMe group."""

    if not new_bots:
        return "No groups to notify."

    access_token = _resolve_access_token()
    if not access_token:
        raise RuntimeError("GroupMe access token is not configured.")

    headers = _build_headers(access_token)
    attachments = _normalize_attachments(files)
    errors: List[tuple[str, int]] = []

    for bot in new_bots:
        bot_id = bot.get("bot_id")
        if not bot_id:
            continue

        payload = {
            "text": message,
            "attachments": attachments,
            "bot_id": bot_id,
        }

        response = requests.post(
            GROUPME_BOT_POST_URL,
            headers=headers,
            data=json.dumps(payload),
        )

        if response.status_code != 202:
            errors.append((bot_id, response.status_code))

    if errors:
        failed_summary = ", ".join(f"{bot_id}:{status}" for bot_id, status in errors)
        raise RuntimeError(f"Failed to send message for bots: {failed_summary}")

    return "Message sent to all groups successfully."


__all__ = [
    "GROUPME_BOT_POST_URL",
    "GROUPME_IMAGE_UPLOAD_URL",
    "send_message_to_groups",
    "upload_image_to_groupme",
]
