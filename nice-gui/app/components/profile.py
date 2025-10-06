"""Profile management view."""

from __future__ import annotations

from nicegui import ui

from ..state import DashboardState


def render_profile_card(state: DashboardState) -> None:
    """Render profile details sourced from the tenant user model."""

    user = state.user
    with ui.card().classes("w-full border border-gray-200 shadow-sm"):
        with ui.column().classes("gap-3"):
            ui.label("Profile Overview").classes("text-lg font-semibold")
            with ui.row().classes("items-center gap-3"):
                initials = (user.nickname or "?")[:2].upper()
                ui.avatar(initials).classes("bg-primary-100 text-primary-600")
                with ui.column().classes("gap-1"):
                    ui.label(user.nickname).classes("text-base font-medium")
                    if user.email:
                        ui.label(user.email).classes("text-sm text-gray-500")
            with ui.row().classes("gap-4 flex-wrap"):
                ui.chip(f"Timezone · {user.timezone}").classes(
                    "bg-gray-100 text-gray-700 text-xs"
                )
                ui.chip(
                    "Contact · "
                    + user.preferred_contact_method.value.replace("_", " ").title()
                ).classes("bg-gray-100 text-gray-700 text-xs")
                ui.chip(
                    "2FA · Enabled" if user.two_factor_enabled else "2FA · Disabled"
                ).classes(
                    "bg-green-100 text-green-700 text-xs"
                    if user.two_factor_enabled
                    else "bg-orange-100 text-orange-700 text-xs"
                )
