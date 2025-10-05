"""Utilities for migrating GroupMe members between groups."""
from __future__ import annotations

import json
from typing import Iterable, List, Sequence

import requests
from requests import RequestException

API_ROOT = "https://api.groupme.com/v3"


def _build_url(path: str, access_token: str) -> str:
    return f"{API_ROOT}{path}?token={access_token}"


def fetch_group_members(group_id: str, access_token: str) -> List[dict]:
    """Fetch members for a given group, returning an empty list on failure."""

    url = _build_url(f"/groups/{group_id}", access_token)
    try:
        response = requests.get(url)
    except RequestException:
        return []

    payload = getattr(response, "text", "{}")
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []

    members = data.get("response", {}).get("members", [])
    return list(members or [])


def _format_member(member: dict) -> dict:
    return {
        "nickname": member.get("nickname", ""),
        "user_id": member.get("user_id", ""),
    }


def add_members_to_group(
    group_id: str,
    members: Iterable[dict],
    access_token: str,
) -> bool:
    """Add the provided members to a group.

    Returns ``True`` when the request is dispatched without raising an error.
    """

    url = _build_url(f"/groups/{group_id}/members/add", access_token)
    headers = {"Content-Type": "application/json"}
    payload = {"members": [_format_member(member) for member in members]}

    try:
        requests.post(url, headers=headers, data=json.dumps(payload))
    except RequestException:
        return False
    return True


def migrate_users(
    original_group_id: str,
    target_group_id: str,
    access_token: str,
) -> Sequence[dict]:
    """Migrate members from ``original_group_id`` into ``target_group_id``."""

    members = fetch_group_members(original_group_id, access_token)
    for member in members:
        add_members_to_group(target_group_id, [member], access_token)
    return members


__all__ = [
    "API_ROOT",
    "add_members_to_group",
    "fetch_group_members",
    "migrate_users",
]
