from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field

class PlanTier(str, Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Plan(BaseModel):
    """Represents a subscription plan for tenants."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Primary key for the Plan")
    name: str = Field(..., description="Plan name (e.g., 'Basic', 'Pro')")
    tier: PlanTier = Field(..., description="Plan tier level")
    description: str = Field(..., description="Description of the plan features")

    # Pricing
    price_cents: int = Field(..., description="Monthly price in cents")
    currency: str = Field(default="USD", description="Currency code")

    # Feature Limits
    max_groups: int = Field(..., description="Maximum number of GroupMe groups")
    max_users_per_group: int = Field(..., description="Maximum users per group")
    ai_credits_per_month: int = Field(..., description="AI credits allocated per month")
    max_custom_commands: int = Field(..., description="Maximum custom commands per group")
    moderation_level: str = Field(default="standard", description="Moderation strictness level")

    # Features
    features: Dict[str, Any] = Field(default_factory=dict, description="Feature flags and settings")

    is_active: bool = Field(default=True, description="Whether the plan is available for subscription")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class Subscription(BaseModel):
    """Represents a tenant's active subscription."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Primary key for the Subscription")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")
    plan_id: uuid.UUID = Field(..., description="Foreign key to the subscribed Plan")

    status: str = Field(default="active", description="Subscription status (active, canceled, expired)")

    # Billing
    current_period_start: datetime = Field(default_factory=datetime.utcnow)
    current_period_end: datetime = Field(...)
    cancel_at_period_end: bool = Field(default=False, description="Cancel at the end of current period")

    # Usage Tracking
    ai_credits_used: int = Field(default=0, description="AI credits consumed this month")
    groups_created: int = Field(default=0, description="Number of groups created")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional subscription metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
