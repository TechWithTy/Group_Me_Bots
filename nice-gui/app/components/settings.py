"""Interactive settings controls."""

from __future__ import annotations

from typing import Iterable

from nicegui import ui

from _schema.schemas.users import NotificationType

from ..state import DashboardState


def render_settings_panel(state: DashboardState) -> None:
    """Render switches for notification preferences and security settings."""

    with ui.card().classes("w-full max-w-md"):
        ui.label("Settings").classes("text-lg font-semibold")
        ui.label(
            "Tune notification channels and security without leaving the dashboard."
        ).classes("text-sm text-gray-600")

        _render_notification_switches(state)
        _render_security_controls(state)


def _render_notification_switches(state: DashboardState) -> None:
    preferences = state.user.notification_preferences
    ui.label("Notifications").classes("text-sm font-medium mt-3")
    for notification in _sorted_notifications(preferences.keys()):
        switch = ui.switch(
            state.notification_label(notification),
            value=bool(preferences.get(notification, False)),
        )
        switch.on_value_change(
            lambda event, item=notification: state.update_notification(
                item, bool(event.value)
            )
        )


def _render_security_controls(state: DashboardState) -> None:
    ui.label("Security").classes("text-sm font-medium mt-4")
    two_factor_switch = ui.switch(
        "Two-factor authentication", value=state.user.two_factor_enabled
    )
    two_factor_switch.on_value_change(
        lambda event: state.set_two_factor(bool(event.value))
    )


def _sorted_notifications(notifications: Iterable[NotificationType]) -> Iterable[NotificationType]:
    """Return notifications sorted for deterministic rendering."""

    return sorted(notifications, key=lambda item: item.value)
