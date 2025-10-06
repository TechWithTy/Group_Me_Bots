"""Shared in-memory state used by the Signal API endpoints."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict

from .models import Account, ApiConfiguration, Attachment


@dataclass
class SignalState:
    configuration: ApiConfiguration = field(default_factory=ApiConfiguration)
    accounts: Dict[str, Account] = field(default_factory=dict)
    attachments: Dict[str, Attachment] = field(default_factory=dict)
    attachment_seq: itertools.count = field(default_factory=lambda: itertools.count(1))
    group_seq: itertools.count = field(default_factory=lambda: itertools.count(1))

    def reset(self) -> None:
        self.configuration = ApiConfiguration()
        self.accounts.clear()
        self.attachments.clear()
        self.attachment_seq = itertools.count(1)
        self.group_seq = itertools.count(1)

    def next_attachment_id(self) -> str:
        return f"attachment_{next(self.attachment_seq)}"

    def next_group_id(self) -> str:
        return f"group-{next(self.group_seq)}"

    def store_attachment(self, content: str, content_type: str) -> str:
        identifier = self.next_attachment_id()
        self.attachments[identifier] = Attachment(identifier, content, content_type)
        return identifier


state = SignalState()

