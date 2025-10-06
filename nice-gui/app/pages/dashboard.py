"""Dashboard composition for the NiceGUI application."""

from __future__ import annotations

from nicegui import ui

from ..components.activity import render_activity_log
from ..components.assistants import render_ai_assistants
from ..components.auth import render_authentication
from ..components.bots import BotManagementView, render_bot_management
from ..components.credits import render_credit_summary
from ..components.profile import render_profile_card
from ..components.settings import render_settings_panel
from ..state import DashboardState, Role


def render_dashboard() -> None:
    """Render the complete operations control center."""

    state = DashboardState.demo()
    ui.page_title("Operations Control Center")

    with ui.column().classes("w-full max-w-6xl mx-auto gap-6 pb-10"):
        with ui.card().classes(
            "w-full border border-gray-200 shadow-sm bg-white/80 backdrop-blur"
        ):
            with ui.column().classes("gap-3"):
                ui.label("Operations Control Center").classes(
                    "text-2xl font-semibold"
                )
                ui.label(
                    "Coordinate profiles, automation, and credits in a single workspace."
                ).classes("text-sm text-gray-500")

                with ui.row().classes(
                    "items-center justify-between gap-3 flex-wrap"
                ):
                    role_label = ui.label(f"Current role: {state.role}").classes(
                        "text-sm text-gray-600"
                    )
                    summary_label = ui.label(state.bot_summary()).classes(
                        "text-sm text-gray-600"
                    )

                def refresh_summary() -> None:
                    summary_label.set_text(state.bot_summary())

                with ui.row().classes("gap-2 flex-wrap"):
                    ui.button(
                        "View as User", on_click=lambda: state.set_role(Role.USER)
                    ).props("color=primary")
                    ui.button(
                        "View as Admin", on_click=lambda: state.set_role(Role.ADMIN)
                    ).props("color=accent")

        bot_view_holder: dict[str, BotManagementView | None] = {"view": None}

        with ui.row().classes("w-full gap-6 flex-col xl:flex-row"):
            with ui.column().classes("flex-1 gap-4 w-full"):
                tabs = ui.tabs(
                    {
                        "profile": "Profile",
                        "settings": "Settings",
                        "bots": "Bots",
                        "assistants": "AI Assistants",
                    },
                    value="profile",
                ).classes("w-full bg-white/80 border border-gray-200 rounded-lg")

                with ui.tab_panels(tabs, value="profile").classes(
                    "w-full bg-white/90 border border-gray-200 rounded-lg"
                ):
                    with ui.tab_panel("profile"):
                        with ui.column().classes("gap-4 p-4"):
                            render_profile_card(state)
                            render_authentication(state)

                    with ui.tab_panel("settings"):
                        with ui.column().classes("gap-4 p-4"):
                            render_settings_panel(state)

                    with ui.tab_panel("bots"):
                        with ui.column().classes("gap-4 p-4"):
                            bot_view_holder["view"] = render_bot_management(
                                state, refresh_summary
                            )

                    with ui.tab_panel("assistants"):
                        with ui.column().classes("gap-4 p-4"):
                            render_ai_assistants(state)

            with ui.column().classes("w-full xl:max-w-sm gap-4"):
                render_credit_summary(state)
                render_activity_log(state)

    def handle_role_change(role: str) -> None:
        role_label.set_text(f"Current role: {role}")
        view = bot_view_holder["view"]
        if view is not None:
            view.apply_role(role)

    state.subscribe_role(handle_role_change)
