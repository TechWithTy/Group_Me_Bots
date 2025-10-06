"""Connections management component."""

from __future__ import annotations

from nicegui import ui

from ..state import DashboardState


def render_connections(state: DashboardState) -> None:
    """Render the connections management interface."""

    with ui.card().classes("w-full border border-gray-200 shadow-sm"):
        ui.label("External Connections").classes("text-lg font-semibold")
        ui.label("Manage integrations with external platforms and services.").classes(
            "text-sm text-gray-600"
        )

        with ui.column().classes("gap-4 mt-4"):
            # Placeholder for connections management
            # This could include API keys, webhook URLs, OAuth configurations, etc.
            with ui.card().classes("w-full bg-blue-50 border border-blue-200"):
                ui.label("🔗 Connection Management").classes("text-md font-medium text-blue-800")
                ui.label("Configure external service integrations and API connections.").classes(
                    "text-sm text-blue-600"
                )

            # Example connection types (this would be expanded based on requirements)
            with ui.expansion("Platform APIs", icon="api").classes("w-full"):
                ui.label("Configure API keys and endpoints for external platforms.").classes(
                    "text-sm text-gray-600"
                )

            with ui.expansion("Webhooks", icon="webhook").classes("w-full"):
                ui.label("Set up webhook endpoints for receiving external notifications.").classes(
                    "text-sm text-gray-600"
                )

            with ui.expansion("OAuth Integrations", icon="security").classes("w-full"):
                ui.label("Manage OAuth applications and authentication flows.").classes(
                    "text-sm text-gray-600"
                )
