from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr

class ContactMethod(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP = "in_app"

class NotificationType(str, Enum):
    MODERATION_ALERTS = "moderation_alerts"
    GROUP_MESSAGES = "group_messages"
    ORDER_UPDATES = "order_updates"
    SYSTEM_ANNOUNCEMENTS = "system_announcements"
    SECURITY_ALERTS = "security_alerts"

class User(BaseModel):
    """Represents a user within the GORT-AI system, linked to a tenant."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Internal primary key for the User")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant this user belongs to")
    groupme_user_id: str = Field(..., description="The user's ID from GroupMe", index=True)

    # Basic Info
    nickname: str
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    timezone: str = Field(default="UTC", description="User's timezone for scheduling")

    # Contact Preferences
    preferred_contact_method: ContactMethod = Field(default=ContactMethod.IN_APP, description="Preferred method for notifications")
    notification_preferences: Dict[NotificationType, bool] = Field(
        default_factory=lambda: {
            NotificationType.MODERATION_ALERTS: True,
            NotificationType.GROUP_MESSAGES: True,
            NotificationType.ORDER_UPDATES: True,
            NotificationType.SYSTEM_ANNOUNCEMENTS: False,
            NotificationType.SECURITY_ALERTS: True,
        },
        description="Granular notification preferences by type"
    )

    # Trust & Moderation
    trust_score: float = Field(default=0.0, description="Computed trust score from the moderation module")

    # Security
    two_factor_enabled: bool = Field(default=False, description="Whether 2FA is enabled for the user")
    last_login_at: Optional[datetime] = None
    login_attempts: int = Field(default=0, description="Number of failed login attempts")
    locked_until: Optional[datetime] = None
    password_hash: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None

    # Subscription & Billing
    subscription_id: Optional[uuid.UUID] = None
    current_plan_id: Optional[uuid.UUID] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GroupMember(BaseModel):
    """Represents individual users in a group."""
    id: str = Field(..., description="Unique ID for the member")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")
    group_id: str = Field(..., description="Foreign key to the GroupChat")

    member_username: str = Field(..., description="The member's username")
    join_date: datetime = Field(..., description="When the member joined the group")
    is_paid_subscriber: bool = Field(default=False, description="Whether the member has a subscription for premium features")

    # User details (optional link to User model)
    user_id: Optional[uuid.UUID] = Field(None, description="Link to User model if applicable")

    # Activity and engagement
    last_activity: Optional[datetime] = None
    message_count: int = Field(default=0, description="Number of messages sent by this member")
    engagement_score: float = Field(default=0.0, description="Calculated engagement score")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional member metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
