"""Dashboard composition for the NiceGUI application."""

from __future__ import annotations

from nicegui import ui

from ..components.activity import render_activity_log
from ..components.bots import render_bot_management
from ..components.credits import render_credit_summary
from ..components.profile import render_profile_card
from ..components.settings import render_settings_panel
from ..state import DashboardState, Role


def render_dashboard() -> None:
    """Render the complete operations control center."""

    state = DashboardState.demo()
    ui.page_title("Operations Control Center")

    with ui.column().classes("gap-4 w-full"):
        ui.label("Operations Control Center").classes("text-2xl font-semibold")
        ui.label(
            "Coordinate profiles, settings, automations, and credits in one view."
        ).classes("text-sm text-gray-500")

        role_label = ui.label(f"Current role: {state.role}").classes(
            "text-sm text-gray-600"
        )
        summary_label = ui.label(state.bot_summary()).classes(
            "text-sm text-gray-600"
        )

        def refresh_summary() -> None:
            summary_label.set_text(state.bot_summary())

        with ui.row().classes("gap-2"):
            ui.button("View as User", on_click=lambda: state.set_role(Role.USER)).props(
                "color=primary"
            )
            ui.button("View as Admin", on_click=lambda: state.set_role(Role.ADMIN)).props(
                "color=accent"
            )

        with ui.row().classes("items-start gap-4 flex-wrap"):
            with ui.column().classes("gap-4"):
                bot_view = render_bot_management(state, refresh_summary)
                render_activity_log(state)
            with ui.column().classes("gap-4"):
                render_profile_card(state)
                render_settings_panel(state)
                render_credit_summary(state)

    def handle_role_change(role: str) -> None:
        role_label.set_text(f"Current role: {role}")
        bot_view.apply_role(role)

    state.subscribe_role(handle_role_change)
