"""Shared helper utilities for Signal API endpoints."""

from __future__ import annotations

from typing import Iterable

from .state import state
from .state.models import Account, GroupPermissions
from .state.utils import now_ms, placeholder_image


def ensure_account(number: str) -> Account:
    account = state.accounts.get(number)
    if account is None:
        account = Account(number=number)
        state.accounts[number] = account
    return account


def assign_group_permissions(data: dict | None) -> GroupPermissions | None:
    if not data:
        return None
    return GroupPermissions(**data)


def add_members(collection: set[str], members: Iterable[str]) -> None:
    collection.update(members)


__all__ = [
    "ensure_account",
    "assign_group_permissions",
    "now_ms",
    "placeholder_image",
    "add_members",
    "state",
]

