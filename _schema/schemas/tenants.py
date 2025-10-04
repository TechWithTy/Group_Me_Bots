from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Tenant(BaseModel):
    """Represents a single customer account in the SaaS platform."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Primary key for the Tenant")
    name: str = Field(..., description="The name of the customer's organization")
    api_key: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique API key for tenant-specific access")
    is_active: bool = Field(default=True, description="Whether the tenant's account is active")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
