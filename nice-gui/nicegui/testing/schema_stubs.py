"""Schema shims that keep the simulator independent of external dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4
import sys
import types


def inject_schema_stubs() -> None:
    """Provide lightweight schema stand-ins when Pydantic is unavailable."""

    if "_schema" not in sys.modules:
        schema_pkg = types.ModuleType("_schema")
        schema_pkg.__path__ = []  # type: ignore[attr-defined]
        sys.modules["_schema"] = schema_pkg
    schema_pkg = sys.modules["_schema"]

    if "_schema.schemas" not in sys.modules:
        schemas_pkg = types.ModuleType("_schema.schemas")
        schemas_pkg.__path__ = []  # type: ignore[attr-defined]
        sys.modules["_schema.schemas"] = schemas_pkg
        schema_pkg.schemas = schemas_pkg  # type: ignore[attr-defined]
    schemas_pkg = sys.modules["_schema.schemas"]

    if "_schema.schemas.bots" not in sys.modules:
        bots_module = types.ModuleType("_schema.schemas.bots")

        @dataclass
        class ChatBot:
            id: str
            tenant_id: str
            bot_name: str
            bot_model: str
            function: str
            monetization_source_id: str
            capabilities: List[str]
            settings: Dict[str, object]
            is_active: bool = False

        bots_module.ChatBot = ChatBot
        sys.modules["_schema.schemas.bots"] = bots_module
        schemas_pkg.bots = bots_module  # type: ignore[attr-defined]

    if "_schema.schemas.subscriptions" not in sys.modules:
        subs_module = types.ModuleType("_schema.schemas.subscriptions")

        class PlanTier(str, Enum):
            BASIC = "basic"
            PRO = "pro"
            ENTERPRISE = "enterprise"

        @dataclass
        class Plan:
            name: str
            tier: PlanTier
            description: str
            price_cents: int
            currency: str
            max_groups: int
            max_users_per_group: int
            ai_credits_per_month: int
            max_custom_commands: int
            moderation_level: str
            features: Dict[str, object]
            id: str = field(default_factory=lambda: uuid4().hex)

        @dataclass
        class Subscription:
            tenant_id: str
            plan_id: str
            current_period_end: datetime
            ai_credits_used: int
            id: str = field(default_factory=lambda: uuid4().hex)

        subs_module.PlanTier = PlanTier
        subs_module.Plan = Plan
        subs_module.Subscription = Subscription
        sys.modules["_schema.schemas.subscriptions"] = subs_module
        schemas_pkg.subscriptions = subs_module  # type: ignore[attr-defined]

    if "_schema.schemas.users" not in sys.modules:
        users_module = types.ModuleType("_schema.schemas.users")

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

        @dataclass
        class User:
            tenant_id: str
            groupme_user_id: str
            nickname: str
            email: Optional[str]
            timezone: str
            preferred_contact_method: ContactMethod
            two_factor_enabled: bool
            notification_preferences: Dict[NotificationType, bool] = field(
                default_factory=dict
            )

        users_module.ContactMethod = ContactMethod
        users_module.NotificationType = NotificationType
        users_module.User = User
        sys.modules["_schema.schemas.users"] = users_module
        schemas_pkg.users = users_module  # type: ignore[attr-defined]
