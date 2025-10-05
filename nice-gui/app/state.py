"""State management and domain models for the operations dashboard."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Deque, List, Sequence
from uuid import uuid4

from _schema.schemas.bots import ChatBot
from _schema.schemas.subscriptions import Plan, PlanTier, Subscription
from _schema.schemas.users import ContactMethod, NotificationType, User

from .controllers import BotController


class Role:
    """Simple role enumeration."""

    ADMIN = "Admin"
    USER = "User"


@dataclass
class DashboardState:
    """Aggregated state for the operations dashboard."""

    user: User
    plan: Plan
    subscription: Subscription
    bots: Sequence[ChatBot]
    bot_controller: BotController
    role: str = Role.USER
    activation_credit_cost: int = 40

    def __post_init__(self) -> None:
        self.activity_log: Deque[str] = deque(maxlen=8)
        self._activity_listeners: List[Callable[[List[str]], None]] = []
        self._credit_listeners: List[Callable[[int, int], None]] = []
        self._role_listeners: List[Callable[[str], None]] = []

        self.bot_controller.subscribe_log(self._log)
        for bot in self.bots:
            self.bot_controller.subscribe_status(
                bot.bot_name, self._handle_status_update(bot.bot_name)
            )

    # Construction helpers -------------------------------------------------
    @classmethod
    def demo(cls) -> "DashboardState":
        """Create demo data derived from repository schemas."""

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
        return cls(user=user, plan=plan, subscription=subscription, bots=bots, bot_controller=controller)

    # Observers ------------------------------------------------------------
    def subscribe_activity(self, callback: Callable[[List[str]], None]) -> None:
        """Subscribe to activity log updates."""

        self._activity_listeners.append(callback)
        callback(list(self.activity_log))

    def subscribe_credits(self, callback: Callable[[int, int], None]) -> None:
        """Subscribe to credit usage updates."""

        self._credit_listeners.append(callback)
        callback(self.subscription.ai_credits_used, self.plan.ai_credits_per_month)

    def subscribe_role(self, callback: Callable[[str], None]) -> None:
        """Subscribe to role changes."""

        self._role_listeners.append(callback)
        callback(self.role)

    # Mutators -------------------------------------------------------------
    def set_role(self, role: str) -> None:
        """Update the active role and notify observers."""

        if self.role == role:
            return
        self.role = role
        self._log(f"Switched to {role} mode")
        for callback in self._role_listeners:
            callback(role)

    def toggle_bot(self, bot_name: str, active: bool) -> None:
        """Toggle a bot via the controller."""

        self.bot_controller.set_status(bot_name, active)

    def update_notification(self, notification: NotificationType, enabled: bool) -> None:
        """Persist notification preferences and log the change."""

        self.user.notification_preferences[notification] = enabled
        state = "enabled" if enabled else "disabled"
        self._log(f"{self.notification_label(notification)} notifications {state}")

    def set_two_factor(self, enabled: bool) -> None:
        """Persist two-factor authentication preference."""

        if self.user.two_factor_enabled == enabled:
            return
        self.user.two_factor_enabled = enabled
        state = "enabled" if enabled else "disabled"
        self._log(f"Two-factor authentication {state}")

    # Derived data ---------------------------------------------------------
    def bot_summary(self) -> str:
        """Return a human friendly automation summary."""

        return (
            f"Active automations: {self.bot_controller.count_active()} of {self.bot_controller.total()}"
        )

    def credit_summary(self) -> str:
        """Return the current credit usage string."""

        return (
            f"Credits used: {self.subscription.ai_credits_used} / {self.plan.ai_credits_per_month}"
        )

    def notification_label(self, notification: NotificationType) -> str:
        """Return a human friendly notification label."""

        return notification.value.replace("_", " ").capitalize()

    # Internals ------------------------------------------------------------
    def _log(self, message: str) -> None:
        self.activity_log.appendleft(message)
        for callback in self._activity_listeners:
            callback(list(self.activity_log))

    def _handle_status_update(self, bot_name: str) -> Callable[[bool], None]:
        def handler(active: bool) -> None:
            delta = self.activation_credit_cost if active else -self.activation_credit_cost
            self.subscription.ai_credits_used = max(
                0,
                min(
                    self.plan.ai_credits_per_month,
                    self.subscription.ai_credits_used + delta,
                ),
            )
            for callback in self._credit_listeners:
                callback(
                    self.subscription.ai_credits_used, self.plan.ai_credits_per_month
                )

        return handler
