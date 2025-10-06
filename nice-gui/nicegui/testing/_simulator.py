"""Simulator utilities that replace the NiceGUI runtime for tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import sys

from .schema_stubs import inject_schema_stubs

APP_ROOT = Path(__file__).resolve().parents[2]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

try:  # pragma: no cover - executed at import time
    from app.state import DashboardState, Role
except Exception:  # pragma: no cover - fallback when schemas fail to import
    inject_schema_stubs()
    from app.state import DashboardState, Role


@dataclass
class _Element:
    """Lightweight element wrapper exposed through ``User.find``."""

    session: "_DashboardSession"
    label: str

    def click(self) -> None:
        """Simulate clicking the element."""

        self.session.handle_click(self.label)

    def type(self, value: str) -> None:
        """Simulate typing into an input element."""

        self.session.handle_type(self.label, value)


class User:
    """Simulate an interactive NiceGUI test user."""

    def __init__(self) -> None:
        self._session: Optional[_DashboardSession] = None

    def open(self, path: str) -> None:
        """Open a dashboard path and initialise the session state."""

        if path != "/":  # pragma: no cover - tests only open the dashboard root.
            raise ValueError("Only the root path is supported in the simulator")
        self._session = _DashboardSession()

    def should_see(self, text: str) -> None:
        """Assert that the current session view contains ``text``."""

        if not self._session:
            raise AssertionError("Session has not been initialised; call open('/') first.")
        if text not in self._session.snapshot:
            raise AssertionError(f"Expected to see '{text}' but it was absent.")

    def find(self, label: str) -> _Element:
        """Return a simulated element that can be clicked or typed into."""

        if not self._session:
            raise AssertionError("Session has not been initialised; call open('/') first.")
        if label not in self._session.interactive_labels:
            raise AssertionError(f"No element with label '{label}' exists in the simulator.")
        return _Element(session=self._session, label=label)


class _DashboardSession:
    """Stateful simulation of the dashboard page."""

    def __init__(self) -> None:
        self.state = DashboardState.demo()
        self.selected_amount = 25
        self.checkout_session: Optional[str] = None
        self.checkout_status: str = ""
        self.checkout_link_ready = False
        self._auth_inputs: Dict[str, str] = {"Dice Email": "", "Password": ""}
        self._activity: List[str] = []
        self._credit_summary = self.state.credit_summary()
        self._addon_credits = 0
        self._auth_status = self.state.auth.status_text()
        self._notification_labels = {
            self.state.notification_label(notification): notification
            for notification in self.state.user.notification_preferences
        }
        self.tab_labels = (
            "Bots & Automations",
            "User Profile",
            "User Settings",
            "Connections",
            "AI Assistants & Billing",
        )
        self.active_tab = self.tab_labels[0]

        self.state.subscribe_activity(self._set_activity)
        self.state.subscribe_credits(self._set_credits)
        self.state.subscribe_auth(self._set_auth_status)

    # ------------------------------------------------------------------
    @property
    def snapshot(self) -> str:
        """Return a newline joined snapshot of the dashboard view."""

        lines = [
            "Operations Control Center",
            *self.tab_labels,
            f"Current role: {self.state.role}",
            self.state.bot_summary(),
        ]

        lines.extend(self._tab_snapshot())

        if self.active_tab == "AI Assistants & Billing" and self._addon_credits:
            lines.append(f"Add-on credits: {self._addon_credits}")

        if self.active_tab == "AI Assistants & Billing" and self.checkout_status:
            lines.append(self.checkout_status)
        if self.active_tab == "AI Assistants & Billing" and self.checkout_link_ready:
            lines.append("Complete Purchase")

        if self.active_tab == "Bots & Automations":
            lines.extend(self._activity)

        return "\n".join(lines)

    @property
    def interactive_labels(self) -> Iterable[str]:
        """Labels that ``User.find`` can target."""

        bot_controls = [f"Toggle {bot.bot_name} automation" for bot in self.state.bots]
        credit_options = [f"{amount} Credits (${amount})" for amount in (10, 25, 50, 100)]
        return [
            "View as User",
            "View as Admin",
            *self.tab_labels,
            *bot_controls,
            "Two-factor authentication",
            "Dice Email",
            "Password",
            "Sign in",
            "Log out",
            "Create checkout session",
            "Confirm payment",
            *credit_options,
        ] + list(self._notification_labels.keys())

    @property
    def _role_helper_text(self) -> str:
        return (
            "Bot controls are unlocked for administrators."
            if self.state.role == Role.ADMIN
            else "Bot controls are locked while in user mode."
        )

    def _bot_status_lines(self) -> List[str]:
        lines = []
        for bot in self.state.bots:
            status = "Active" if self.state.bot_controller.get_status(bot.bot_name) else "Paused"
            lines.append(f"{bot.bot_name} automation status: {status}")
        return lines

    def _tab_snapshot(self) -> List[str]:
        if self.active_tab == "Bots & Automations":
            return [
                "Bot Management",
                self._role_helper_text,
                *self._bot_status_lines(),
                "Recent Activity",
            ]
        if self.active_tab == "User Profile":
            user = self.state.user
            details = [
                "Profile Management",
                f"{user.nickname} ({user.email})" if user.email else user.nickname,
                f"Timezone: {user.timezone}",
                f"Preferred contact: {user.preferred_contact_method.value.replace('_', ' ').title()}",
                "Authentication",
                self._auth_status,
            ]
            details.append(
                "Two-factor authentication is enabled"
                if user.two_factor_enabled
                else "Two-factor authentication is disabled"
            )
            details.append("Profile Configuration")
            details.extend(self._configuration_lines(self.state.profile_sections))
            return details
        if self.active_tab == "User Settings":
            lines = ["Settings", "Notifications", "Security", "Workspace Settings"]
            lines.extend(self._configuration_lines(self.state.settings_sections))
            return lines
        if self.active_tab == "Connections":
            return [
                "Connections",
                *self._configuration_lines(self.state.connection_sections),
            ]
        if self.active_tab == "AI Assistants & Billing":
            lines = ["AI Assistant Overview"]
            lines.extend(self._assistant_lines())
            lines.append("Credits & Billing")
            lines.append(self._credit_summary)
            lines.append("Purchase add-on credits")
            lines.append(f"Selected package: {self.selected_amount} credits")
            return lines
        return []

    def _assistant_lines(self) -> List[str]:
        lines: List[str] = []
        for bot in self.state.bots:
            lines.append(f"{bot.bot_name} ({bot.bot_model})")
            lines.append(
                f"Focus: {bot.function.replace('_', ' ').title()}"
            )
            capabilities = [cap.replace("_", " ").title() for cap in bot.capabilities]
            if capabilities:
                lines.append("Capabilities: " + ", ".join(capabilities))
            settings_pairs = [
                f"{key.replace('_', ' ').title()}: {value}"
                for key, value in bot.settings.items()
            ]
            if settings_pairs:
                lines.extend(settings_pairs)
            status = "Active" if self.state.bot_controller.get_status(bot.bot_name) else "Paused"
            lines.append(f"Status: {status}")
        return lines

    def _configuration_lines(self, sections) -> List[str]:
        lines: List[str] = []
        for section in sections:
            lines.append(section.title)
            for key, value in section.items:
                rendered_value = value if value else "Not configured"
                lines.append(f"{key}: {rendered_value}")
        return lines

    # ------------------------------------------------------------------
    def handle_click(self, label: str) -> None:
        if label == "View as Admin":
            self.state.set_role(Role.ADMIN)
            return
        if label == "View as User":
            self.state.set_role(Role.USER)
            return
        if label == "Log out":
            self.state.logout()
            return
        if label == "Sign in":
            self.state.authenticate_with_dice(
                self._auth_inputs["Dice Email"], self._auth_inputs["Password"]
            )
            self._auth_inputs["Dice Email"] = ""
            self._auth_inputs["Password"] = ""
            return
        if label in self.tab_labels:
            self.active_tab = label
            return
        if label == "Create checkout session":
            session_id, _url = self.state.create_checkout_session(self.selected_amount)
            self.checkout_session = session_id
            self.checkout_status = f"Checkout ready for {self.selected_amount} credits"
            self.checkout_link_ready = True
            return
        if label == "Confirm payment":
            if not self.checkout_session:
                return
            amount = self.state.complete_checkout(self.checkout_session)
            self.checkout_status = (
                f"Payment successful! {amount} credits added to your account."
            )
            self.checkout_session = None
            self.checkout_link_ready = False
            return
        if label in self._notification_labels:
            notification = self._notification_labels[label]
            current = bool(self.state.user.notification_preferences.get(notification, False))
            self.state.update_notification(notification, not current)
            return
        if label == "Two-factor authentication":
            self.state.set_two_factor(not self.state.user.two_factor_enabled)
            return
        if label.startswith("Toggle ") and label.endswith(" automation"):
            bot_name = label.removeprefix("Toggle ").removesuffix(" automation")
            if self.state.role != Role.ADMIN:
                return
            active = self.state.bot_controller.get_status(bot_name)
            self.state.toggle_bot(bot_name, not active)
            return
        if label in {"10 Credits ($10)", "25 Credits ($25)", "50 Credits ($50)", "100 Credits ($100)"}:
            self.selected_amount = int(label.split()[0])
            return
        raise AssertionError(f"Unhandled element click for label '{label}'")

    def handle_type(self, label: str, value: str) -> None:
        if label in self._auth_inputs:
            self._auth_inputs[label] = value
            return
        raise AssertionError(f"Cannot type into label '{label}'")

    # ------------------------------------------------------------------
    def _set_activity(self, entries: List[str]) -> None:
        self._activity = entries

    def _set_credits(self, used: int, limit: int, addon: int) -> None:
        summary = f"Credits used: {used} / {limit}"
        if addon:
            summary = f"{summary} | Add-on credits: {addon}"
        self._credit_summary = summary
        self._addon_credits = addon

    def _set_auth_status(self, auth_state) -> None:
        self._auth_status = auth_state.status_text()
