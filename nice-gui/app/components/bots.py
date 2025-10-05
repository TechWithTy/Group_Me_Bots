"""Bot management controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from nicegui import ui

from ..controllers import BotController
from ..state import DashboardState, Role


@dataclass
class BotManagementView:
    """Hold references that react to role changes."""

    toggles: Dict[str, ui.switch]
    helper_label: ui.label

    def apply_role(self, role: str) -> None:
        """Enable or disable switches depending on the active role."""

        for switch in self.toggles.values():
            if role == Role.ADMIN:
                switch.enable()
            else:
                switch.disable()
        if role == Role.ADMIN:
            self.helper_label.set_text("Bot controls are unlocked for administrators.")
        else:
            self.helper_label.set_text("Bot controls are locked while in user mode.")


def render_bot_management(
    state: DashboardState, on_status_change: Callable[[], None]
) -> BotManagementView:
    """Render automation toggles and wire up observers."""

    controller: BotController = state.bot_controller
    toggles: Dict[str, ui.switch] = {}

    with ui.card().classes("w-full max-w-xl"):
        ui.label("Bot Management").classes("text-lg font-semibold")
        helper_label = ui.label("").classes("text-sm text-gray-600")

        for bot in state.bots:
            status_label = ui.label(
                f"{bot.bot_name} automation status: {'Active' if controller.get_status(bot.bot_name) else 'Paused'}"
            ).classes("text-sm")
            toggle = ui.switch(
                f"Toggle {bot.bot_name} automation",
                value=controller.get_status(bot.bot_name),
            )

            def handle_change(event, name=bot.bot_name) -> None:
                state.toggle_bot(name, bool(event.value))

            toggle.on_value_change(handle_change)
            toggles[bot.bot_name] = toggle

            def handle_status_update(active: bool, name=bot.bot_name, label=status_label) -> None:
                label.set_text(
                    f"{name} automation status: {'Active' if active else 'Paused'}"
                )
                on_status_change()

            controller.subscribe_status(bot.bot_name, handle_status_update)

    view = BotManagementView(toggles=toggles, helper_label=helper_label)
    view.apply_role(state.role)
    return view
