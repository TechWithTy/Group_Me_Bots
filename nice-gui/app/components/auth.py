"""Authentication controls for the operations dashboard."""

from __future__ import annotations

from nicegui import ui

from ..state import DashboardState


def render_authentication(state: DashboardState) -> None:
    """Render login, logout, and SaaS token controls."""

    with ui.card().classes("w-full border border-gray-200 shadow-sm"):
        ui.label("Authentication").classes("text-lg font-semibold")
        status_label = ui.label("").classes("text-sm text-gray-600")

        def update_status(auth_state) -> None:
            status_label.set_text(auth_state.status_text())

        state.subscribe_auth(update_status)

        with ui.row().classes("gap-2 mt-2"):
            ui.button("Switch Account", on_click=state.logout).props(
                "color=warning"
            )

        with ui.expansion("Dice Email Login", value=True).classes(
            "mt-2 rounded-lg border border-gray-100"
        ):
            email_input = ui.input("Dice Email", placeholder="you@example.com").classes(
                "w-full"
            )
            password_input = ui.input("Password", password=True).classes("w-full")
            feedback = ui.label("").classes("text-xs text-red-500")

            def handle_login() -> None:
                try:
                    state.authenticate_with_dice(
                        email_input.value or "", password_input.value or ""
                    )
                except ValueError:
                    feedback.set_text("Invalid email or password. Minimum length 6.")
                    return
                feedback.set_text("")
                email_input.value = ""
                password_input.value = ""
                ui.notify("Signed in successfully", type="positive")

            ui.button("Sign in", on_click=handle_login).classes("mt-2")

        with ui.expansion("SaaS Provider Login").classes(
            "mt-2 rounded-lg border border-gray-100"
        ):
            token_input = ui.input("Paste token").classes("w-full")
            link_label = ui.label("").classes("text-xs text-gray-500")

            def handle_generate() -> None:
                url = state.generate_saas_login_url()
                link_label.set_text(f"Complete SaaS login via {url}")

            def handle_token() -> None:
                try:
                    state.authenticate_with_token(token_input.value or "")
                except ValueError:
                    ui.notify("Token required", type="warning")
                    return
                token_input.value = ""
                ui.notify("SaaS token accepted", type="positive")

            ui.button("Get SaaS Login Link", on_click=handle_generate).classes("mt-2")
            ui.button("Apply Token", on_click=handle_token).classes("mt-2")
