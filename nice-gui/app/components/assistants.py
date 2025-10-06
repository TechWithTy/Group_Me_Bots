"""AI assistant overview cards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from nicegui import ui

from ..controllers import BotController
from ..state import DashboardState

_BADGE_BASE = "rounded-full px-2 py-1 text-xs font-medium"


@dataclass
class AssistantOverview:
    """Hold references to update assistant status badges."""

    badges: Dict[str, ui.label]
    controller: BotController

    def apply_status(self, bot_name: str, active: bool) -> None:
        """Update badge text and tone for ``bot_name``."""

        badge = self.badges[bot_name]
        badge.set_text("Active" if active else "Paused")
        tone = "bg-green-100 text-green-700" if active else "bg-orange-100 text-orange-700"
        badge.classes(replace=f"{_BADGE_BASE} {tone}")


def render_ai_assistants(state: DashboardState) -> AssistantOverview:
    """Render AI assistant capabilities and live status."""

    controller = state.bot_controller
    badges: Dict[str, ui.label] = {}

    with ui.card().classes("w-full border border-gray-200 shadow-sm"):
        with ui.column().classes("gap-3"):
            ui.label("AI Assistants").classes("text-lg font-semibold")
            ui.label(
                "Monitor active assistants, their specialties, and supported workflows."
            ).classes("text-sm text-gray-600")

            for bot in state.bots:
                with ui.column().classes(
                    "gap-2 w-full bg-gray-50 border border-gray-100 rounded-lg px-3 py-3"
                ):
                    with ui.row().classes("items-center justify-between"):
                        ui.label(bot.bot_name).classes("text-sm font-medium")
                        badge = ui.label("").classes(_BADGE_BASE)
                        badges[bot.bot_name] = badge

                    ui.label(f"Model · {bot.bot_model}").classes(
                        "text-xs text-gray-500"
                    )
                    ui.label(
                        "Focus · " + bot.function.replace("_", " ").title()
                    ).classes("text-xs text-gray-500")

                    if bot.capabilities:
                        with ui.row().classes("flex-wrap gap-2"):
                            for capability in sorted(bot.capabilities):
                                ui.chip(capability.replace("_", " ").title()).classes(
                                    "bg-white border border-gray-200 text-xs"
                                )

    view = AssistantOverview(badges=badges, controller=controller)

    for bot in state.bots:
        view.apply_status(bot.bot_name, controller.get_status(bot.bot_name))
        controller.subscribe_status(
            bot.bot_name,
            lambda active, name=bot.bot_name: view.apply_status(name, active),
        )

    return view
