"""AI assistant overview cards."""

from __future__ import annotations

from nicegui import ui

from ..state import DashboardState


def render_ai_assistants(state: DashboardState) -> None:
    """Render a grid of AI assistants with their capabilities."""

    controller = state.bot_controller
    with ui.card().classes("w-full max-w-4xl"):
        ui.label("AI Assistant Overview").classes("text-lg font-semibold")
        ui.label(
            "Monitor each assistant's model, focus area, and readiness in one glance."
        ).classes("text-sm text-gray-600")

        with ui.element("div").classes(
            "grid gap-3 mt-4 grid-cols-1 md:grid-cols-2"
        ):
            for bot in state.bots:
                active = controller.get_status(bot.bot_name)
                status_label = "Active" if active else "Paused"
                status_color = "positive" if active else "grey"
                with ui.card().classes(
                    "shadow-none border border-gray-200 dark:border-gray-700 "
                    "rounded-xl bg-white dark:bg-gray-900"
                ):
                    with ui.column().classes("gap-2"):
                        with ui.row().classes(
                            "items-center justify-between gap-2"
                        ):
                            ui.label(bot.bot_name).classes("text-base font-semibold")
                            ui.badge(status_label).props(f"color={status_color}")

                        ui.label(f"Model: {bot.bot_model}").classes(
                            "text-sm text-gray-600"
                        )
                        ui.label(
                            f"Focus: {bot.function.replace('_', ' ').title()}"
                        ).classes("text-sm text-gray-600")

                        if bot.capabilities:
                            ui.label("Capabilities").classes(
                                "text-xs font-semibold text-gray-500 uppercase"
                            )
                            with ui.row().classes("gap-2 flex-wrap"):
                                for capability in bot.capabilities:
                                    ui.chip(capability.replace("_", " ").title()).props(
                                        "color=primary"
                                    ).classes("text-xs")

                        if bot.settings:
                            ui.label("Key settings").classes(
                                "text-xs font-semibold text-gray-500 uppercase"
                            )
                            with ui.column().classes("gap-1"):
                                for key, value in bot.settings.items():
                                    ui.label(f"{key.replace('_', ' ').title()}: {value}").classes(
                                        "text-xs text-gray-600"
                                    )

                        ui.label(
                            "Automation is ready for handoff when enabled."
                        ).classes("text-xs text-gray-500 pt-2")
