"""Dataclasses modelling the Signal API domain for the faux backend."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class LoggingConfiguration:
    level: str = "INFO"


@dataclass
class ApiConfiguration:
    logging: LoggingConfiguration = field(default_factory=LoggingConfiguration)


@dataclass
class Attachment:
    identifier: str
    content: str
    content_type: str


@dataclass
class AccountSettings:
    discoverable_by_number: bool = True
    share_number: bool = True


@dataclass
class Contact:
    uuid: str
    number: str
    name: Optional[str] = None
    profile_key: str = ""
    avatar: str = ""
    expiration_in_seconds: Optional[int] = None


@dataclass
class Device:
    identifier: int
    name: str
    created: int
    last_seen: int
    uri: str


@dataclass
class GroupPermissions:
    add_members: Optional[str] = None
    edit_group: Optional[str] = None
    send_messages: Optional[str] = None


@dataclass
class Group:
    identifier: str
    name: Optional[str]
    description: Optional[str]
    members: Set[str] = field(default_factory=set)
    admins: Set[str] = field(default_factory=set)
    permissions: GroupPermissions = field(default_factory=GroupPermissions)
    group_link: Optional[str] = None
    expiration_time: Optional[int] = None
    blocked: bool = False
    avatar: str = ""


@dataclass
class Identity:
    number: str
    uuid: str
    trust_level: str
    added_timestamp: int


@dataclass
class StickerPack:
    pack_id: str
    pack_key: str
    title: str
    author: str


@dataclass
class Message:
    timestamp: int
    sender: str
    message: str
    recipients: List[str]
    attachments: List[str]
    view_once: bool = False
    sticker: Optional[str] = None


@dataclass
class Receipt:
    receipt_type: str
    recipient: str
    timestamp: int


@dataclass
class Account:
    number: str
    registered: bool = False
    verified: bool = False
    pin: Optional[str] = None
    trust_mode: str = "TRUSTED_UNVERIFIED"
    username: Optional[str] = None
    username_discriminator: Optional[str] = None
    username_link: Optional[str] = None
    settings: AccountSettings = field(default_factory=AccountSettings)
    contacts: Dict[str, Contact] = field(default_factory=dict)
    devices: Dict[int, Device] = field(default_factory=dict)
    next_device_id: int = 1
    groups: Dict[str, Group] = field(default_factory=dict)
    sticker_packs: Dict[str, StickerPack] = field(default_factory=dict)
    identities: Dict[str, Identity] = field(default_factory=dict)
    inbox: List[Message] = field(default_factory=list)
    reactions: Dict[Tuple[str, str, int], str] = field(default_factory=dict)
    rate_limit_events: List[Tuple[str, str, int]] = field(default_factory=list)
    receipts: List[Receipt] = field(default_factory=list)
    typing: Set[str] = field(default_factory=set)
    profile_name: Optional[str] = None
    profile_about: Optional[str] = None
    profile_avatar: Optional[str] = None

