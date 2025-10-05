"""Profile management view."""

from __future__ import annotations

from nicegui import ui

from ..state import DashboardState


def render_profile_card(state: DashboardState) -> None:
    """Render profile details sourced from the tenant user model."""

    user = state.user
    with ui.card().classes("w-full max-w-md"):
        ui.label("Profile Management").classes("text-lg font-semibold")
        ui.label(
            f"{user.nickname} ({user.email})" if user.email else user.nickname
        ).classes("text-sm")
        ui.label(f"Timezone: {user.timezone}").classes("text-sm text-gray-600")
        ui.label(
            f"Preferred contact: {user.preferred_contact_method.value.replace('_', ' ').title()}"
        ).classes("text-sm text-gray-600")
        ui.label(
            "Two-factor authentication is enabled"
            if user.two_factor_enabled
            else "Two-factor authentication is disabled"
        ).classes("text-sm text-gray-600")
