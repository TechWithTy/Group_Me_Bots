from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class Group(BaseModel):
    """Represents a GroupMe group managed by the bot for a specific tenant."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant this group belongs to")
    groupme_group_id: str = Field(..., description="The group's ID from GroupMe", unique=True)

    name: str
    owner_user_id: Optional[uuid.UUID] = Field(None, description="Internal User ID of the group owner")
    settings: Dict[str, Any] = Field(default_factory=dict, description="JSONB field for group-specific settings (e.g., moderation level)")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class GroupChat(BaseModel):
    """Represents a group chat where a bot operates, platform-agnostic."""
    id: str = Field(..., description="Unique ID for the group chat")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    platform: str = Field(..., description="Messaging platform (e.g., Discord, Slack, Telegram)")
    group_name: str = Field(..., description="Name of the group chat")
    creation_date: datetime = Field(..., description="When the group was created")
    member_count: int = Field(..., description="Current number of members")

    # Bot and monetization links
    bot_ids: List[str] = Field(default_factory=list, description="List of bot IDs operating in this group")
    monetization_source_ids: List[str] = Field(default_factory=list, description="Associated monetization sources")

    is_active: bool = Field(default=True, description="Whether the group is currently active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional group metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
