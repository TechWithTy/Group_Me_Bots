"""Dashboard composition for the NiceGUI application."""

from __future__ import annotations

from nicegui import ui

from ..components.activity import render_activity_log
from ..components.assistants import render_ai_assistants
from ..components.auth import render_authentication
from ..components.bots import render_bot_management
from ..components.credits import render_credit_summary
from ..components.configuration import render_configuration_sections
from ..components.profile import render_profile_card
from ..components.settings import render_settings_panel
from ..state import DashboardState, Role


def render_dashboard() -> None:
    """Render the complete operations control center."""

    state = DashboardState.demo()
    ui.page_title("Operations Control Center")

    with ui.column().classes("gap-6 w-full max-w-6xl mx-auto pb-8"):
        with ui.column().classes("gap-1"):
            ui.label("Operations Control Center").classes(
                "text-2xl font-semibold tracking-tight"
            )
            ui.label(
                "Coordinate profiles, automations, and AI operations from a streamlined workspace."
            ).classes("text-sm text-gray-500 max-w-2xl")

        with ui.row().classes("gap-2 flex-wrap items-center"):
            role_label = ui.label(f"Current role: {state.role}").classes(
                "text-sm font-medium text-primary"
            )
            summary_label = ui.label(state.bot_summary()).classes(
                "text-sm font-medium text-accent"
            )

        def refresh_summary() -> None:
            summary_label.set_text(state.bot_summary())

        with ui.row().classes("gap-2 flex-wrap"):
            ui.button("View as User", on_click=lambda: state.set_role(Role.USER)).props(
                "color=primary flat"
            )
            ui.button("View as Admin", on_click=lambda: state.set_role(Role.ADMIN)).props(
                "color=accent"
            )

        with ui.tabs().classes(
            "w-full max-w-6xl overflow-x-auto rounded-xl"
        ) as tabs:
            bots_tab = ui.tab("Bots & Automations", icon="smart_toy")
            profile_tab = ui.tab("User Profile", icon="person")
            settings_tab = ui.tab("User Settings", icon="tune")
            connections_tab = ui.tab("Connections", icon="hub")
            ai_tab = ui.tab("AI Assistants & Billing", icon="auto_awesome")

        with ui.tab_panels(tabs, value=bots_tab).classes("w-full max-w-6xl"):
            with ui.tab_panel(bots_tab):
                with ui.row().classes("items-start gap-4 flex-wrap mt-4"):
                    bot_view = render_bot_management(state, refresh_summary)
                    render_activity_log(state)

            with ui.tab_panel(profile_tab):
                with ui.row().classes("items-start gap-4 flex-wrap mt-4"):
                    render_profile_card(state)
                    render_authentication(state)
                render_configuration_sections(
                    "Profile Configuration",
                    "Review escalation contacts and AI credentials.",
                    state.profile_sections,
                )

            with ui.tab_panel(settings_tab):
                with ui.column().classes("gap-4 mt-4"):
                    render_settings_panel(state)
                    render_configuration_sections(
                        "Workspace Settings",
                        "Platform defaults, feature flags, and operational toggles.",
                        state.settings_sections,
                    )

            with ui.tab_panel(connections_tab):
                with ui.column().classes("gap-4 mt-4"):
                    render_configuration_sections(
                        "Connections",
                        "External services linked to the automation suite.",
                        state.connection_sections,
                    )

            with ui.tab_panel(ai_tab):
                with ui.column().classes("gap-4 mt-4"):
                    render_ai_assistants(state)
                    render_credit_summary(state)

    def handle_role_change(role: str) -> None:
        role_label.set_text(f"Current role: {role}")
        bot_view.apply_role(role)

    state.subscribe_role(handle_role_change)
