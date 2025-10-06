"""State management and domain models for the operations dashboard."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, List, Sequence

from _schema.schemas.bots import ChatBot
from _schema.schemas.subscriptions import Plan, Subscription
from _schema.schemas.users import NotificationType, User

from .controllers import BotController
from .factories import demo_payload
from .models.auth import AuthState
from .services.authentication import AuthenticationController
from .services.billing import CheckoutService


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
    auth: AuthState = field(default_factory=AuthState)
    addon_credits: int = 0

    def __post_init__(self) -> None:
        self.activity_log: Deque[str] = deque(maxlen=8)
        self._activity_listeners: List[Callable[[List[str]], None]] = []
        self._credit_listeners: List[Callable[[int, int, int], None]] = []
        self._role_listeners: List[Callable[[str], None]] = []

        self.bot_controller.subscribe_log(self._log)
        for bot in self.bots:
            self.bot_controller.subscribe_status(
                bot.bot_name, self._handle_status_update(bot.bot_name)
            )

        if not self.auth.is_authenticated:
            self.auth = AuthState(
                is_authenticated=True,
                method="Demo",
                email=self.user.email,
                token="demo-token",
            )

        self.auth_controller = AuthenticationController(
            initial=self.auth,
            default_email=self.user.email,
            on_change=self._set_auth_state,
            log=self._log,
        )
        self.checkout_service = CheckoutService(
            on_change=self._update_addon_credits,
            log=self._log,
        )
        self._set_auth_state(self.auth_controller.state)

    # Construction helpers -------------------------------------------------
    @classmethod
    def demo(cls) -> "DashboardState":
        """Create demo data derived from repository schemas."""

        user, plan, subscription, bots, controller, auth = demo_payload()
        return cls(
            user=user,
            plan=plan,
            subscription=subscription,
            bots=bots,
            bot_controller=controller,
            auth=auth,
        )

    # Observers ------------------------------------------------------------
    def subscribe_activity(self, callback: Callable[[List[str]], None]) -> None:
        """Subscribe to activity log updates."""

        self._activity_listeners.append(callback)
        callback(list(self.activity_log))

    def subscribe_credits(self, callback: Callable[[int, int, int], None]) -> None:
        """Subscribe to credit usage updates."""

        self._credit_listeners.append(callback)
        callback(
            self.subscription.ai_credits_used,
            self.plan.ai_credits_per_month,
            self.addon_credits,
        )

    def subscribe_role(self, callback: Callable[[str], None]) -> None:
        """Subscribe to role changes."""

        self._role_listeners.append(callback)
        callback(self.role)

    def subscribe_auth(self, callback: Callable[[AuthState], None]) -> None:
        """Subscribe to authentication state changes."""

        self.auth_controller.subscribe(callback)

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

    def authenticate_with_dice(self, email: str, password: str) -> None:
        """Authenticate using local Dice credentials."""

        self.auth_controller.authenticate_with_dice(email, password)

    def logout(self) -> None:
        """Reset authentication state."""

        self.auth_controller.logout()

    def generate_saas_login_url(self) -> str:
        """Return a simulated SaaS login URL."""

        return self.auth_controller.generate_saas_login_url()

    def authenticate_with_token(self, token: str) -> None:
        """Authenticate using a returned SaaS token."""

        self.auth_controller.authenticate_with_token(token)

    def create_checkout_session(self, credit_amount: int) -> tuple[str, str]:
        """Create a demo checkout session and return its id and URL."""

        return self.checkout_service.create_session(credit_amount)

    def complete_checkout(self, session_id: str) -> int:
        """Finalize a checkout session and allocate credits."""

        return self.checkout_service.complete(session_id)

    # Derived data ---------------------------------------------------------
    def bot_summary(self) -> str:
        """Return a human friendly automation summary."""

        return (
            f"Active automations: {self.bot_controller.count_active()} of {self.bot_controller.total()}"
        )

    def credit_summary(self) -> str:
        """Return the current credit usage string."""

        base = (
            f"Credits used: {self.subscription.ai_credits_used} / {self.plan.ai_credits_per_month}"
        )
        if self.addon_credits:
            return f"{base} | Add-on credits: {self.addon_credits}"
        return base

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
            self._notify_credit_subscribers()

        return handler

    def _set_auth_state(self, auth: AuthState) -> None:
        self.auth = auth

    def _update_addon_credits(self, addon: int) -> None:
        self.addon_credits = addon
        self._notify_credit_subscribers()

    def _notify_credit_subscribers(self) -> None:
        for callback in self._credit_listeners:
            callback(
                self.subscription.ai_credits_used,
                self.plan.ai_credits_per_month,
                self.addon_credits,
            )
