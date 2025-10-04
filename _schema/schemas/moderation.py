from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field

class Infraction(BaseModel):
    """A log of a moderation action taken against a user."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    group_id: uuid.UUID
    user_id: uuid.UUID

    message_id: str|None = Field(None, description="The GroupMe message ID that caused the infraction")
    action_taken: str = Field(..., description="The action taken (e.g., 'warn', 'kick', 'revert')")
    reason: str|None = None
    severity: float = Field(..., description="A score indicating the severity of the infraction")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
