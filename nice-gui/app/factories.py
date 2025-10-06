"""Factory utilities for constructing dashboard state."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Sequence
from uuid import uuid4

from _schema.schemas.bots import ChatBot
from _schema.schemas.subscriptions import Plan, PlanTier, Subscription
from _schema.schemas.users import ContactMethod, NotificationType, User

from .controllers import BotController
from .models.auth import AuthState


def demo_payload() -> tuple[
    User,
    Plan,
    Subscription,
    Sequence[ChatBot],
    BotController,
    AuthState,
]:
    """Return demo entities to seed the dashboard."""

    tenant_id = uuid4()
    plan = Plan(
        name="Growth",
        tier=PlanTier.PRO,
        description="Automation and analytics for scaling teams",
        price_cents=12900,
        currency="USD",
        max_groups=25,
        max_users_per_group=250,
        ai_credits_per_month=320,
        max_custom_commands=25,
        moderation_level="advanced",
        features={"analytics": True, "sso": True},
    )
    subscription = Subscription(
        tenant_id=tenant_id,
        plan_id=plan.id,
        current_period_end=datetime.utcnow() + timedelta(days=12),
        ai_credits_used=160,
    )
    user = User(
        tenant_id=tenant_id,
        groupme_user_id="ops-admin",
        nickname="Alex Doe",
        email="alex@example.com",
        timezone="US/Eastern",
        preferred_contact_method=ContactMethod.EMAIL,
        two_factor_enabled=True,
    )
    user.notification_preferences = {
        NotificationType.MODERATION_ALERTS: True,
        NotificationType.GROUP_MESSAGES: True,
        NotificationType.ORDER_UPDATES: False,
        NotificationType.SYSTEM_ANNOUNCEMENTS: True,
        NotificationType.SECURITY_ALERTS: True,
    }
    bots = (
        ChatBot(
            id="bot-announcements",
            tenant_id=tenant_id,
            bot_name="Announcements",
            bot_model="gpt-4o-mini",
            function="broadcasts",
            monetization_source_id="sponsorship",
            capabilities=["announcements", "campaigns"],
            settings={"cadence": "daily"},
            is_active=False,
        ),
        ChatBot(
            id="bot-support",
            tenant_id=tenant_id,
            bot_name="Support",
            bot_model="claude-3-sonnet",
            function="customer_support",
            monetization_source_id="support",
            capabilities=["triage", "handoff"],
            settings={"sla_minutes": 5},
            is_active=False,
        ),
        ChatBot(
            id="bot-moderation",
            tenant_id=tenant_id,
            bot_name="Moderation",
            bot_model="gpt-4o",
            function="moderation",
            monetization_source_id="compliance",
            capabilities=["content_filtering"],
            settings={"escalation": "auto"},
            is_active=False,
        ),
    )
    controller = BotController(bots)
    auth = AuthState(is_authenticated=True, method="Demo", email=user.email, token="demo-token")
    return user, plan, subscription, bots, controller, auth
