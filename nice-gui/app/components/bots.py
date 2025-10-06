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

    with ui.card().classes("w-full border border-gray-200 shadow-sm"):
        with ui.column().classes("gap-4"):
            ui.label("Bot Management").classes("text-lg font-semibold")
            ui.label(
                "Manage bots across different channels and platforms."
            ).classes("text-sm text-gray-600")

            # Channel Overview Section
            _render_channel_overview(state, controller)

            # Bot-Channel Assignment Section
            _render_bot_channel_management(state, controller, toggles, on_status_change)

    view = BotManagementView(toggles=toggles, helper_label=ui.label(""))
    view.apply_role(state.role)
    return view


def _render_channel_overview(state: DashboardState, controller: BotController) -> None:
    """Render overview of bots across different channels."""

    # Define available channels
    channels = {
        "GroupMe": ["Tally Main", "Tally Subleasing", "Tally TRVP House", "Tally BLMA"],
        "Discord": ["Main Server", "Development Server"],
        "Telegram": ["Main Group", "Support Group"],
        "Signal": ["Phone 1", "Phone 2"]
    }

    with ui.expansion("Channel Overview", value=True).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-3 w-full"):
            ui.label("Active Bots ■").classes("text-sm font-medium")

            for platform, channel_list in channels.items():
                with ui.card().classes("p-3 border border-gray-200"):
                    ui.label(f"{platform} Channels").classes("text-sm font-semibold text-gray-700")

                    for channel in channel_list:
                        # Get bots active on this channel
                        active_bots = [bot for bot in state.bots
                                     if controller.get_status(bot.bot_name) and
                                     _is_bot_assigned_to_channel(bot.bot_name, channel, platform)]

                        with ui.row().classes("items-center gap-2 w-full"):
                            ui.label(channel).classes("text-sm flex-1")
                            if active_bots:
                                with ui.row().classes("gap-1 flex-wrap"):
                                    for bot in active_bots[:3]:  # Show max 3 bots
                                        # Check if bot has AI assistant connections
                                        assistant_connections = _get_bot_assistant_connections(bot.bot_name)
                                        bot_display = bot.bot_name
                                        if assistant_connections:
                                            bot_display += " 🤖"  # Add AI indicator

                                        ui.chip(bot_display).classes("bg-green-100 text-green-700 text-xs")
                                    if len(active_bots) > 3:
                                        ui.chip(f"+{len(active_bots) - 3} more").classes("bg-gray-100 text-gray-600 text-xs")
                            else:
                                ui.label("No bots active").classes("text-xs text-gray-500")


def _render_bot_channel_management(state: DashboardState, controller: BotController,
                                 toggles: Dict[str, ui.switch],
                                 on_status_change: Callable[[], None]) -> None:
    """Render bot-channel assignment and management controls."""

    with ui.expansion("Bot-Channel Assignment", value=True).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-4 w-full"):
            ui.label("Assign Bots to Channels").classes("text-sm font-medium")

            # Available channels for assignment
            available_channels = {
                "GroupMe": ["Tally Main", "Tally Subleasing", "Tally TRVP House", "Tally BLMA", "Tally 2K23"],
                "Discord": ["Main Server", "Development Server", "Test Server"],
                "Telegram": ["Main Group", "Support Group", "Announcements"],
                "Signal": ["Phone 1", "Phone 2", "Backup Phone"]
            }

def _render_bot_channel_management(state: DashboardState, controller: BotController,
                                 toggles: Dict[str, ui.switch],
                                 on_status_change: Callable[[], None]) -> None:
    """Render bot-channel assignment and management controls."""

    with ui.expansion("Bot-Channel Assignment", value=True).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-4 w-full"):
            ui.label("Assign Bots to Channels").classes("text-sm font-medium")
            ui.label("Configure bot types and assign them to specific channels").classes("text-xs text-gray-600 mb-3")

            # Available channels for assignment
            available_channels = {
                "GroupMe": ["Tally Main", "Tally Subleasing", "Tally TRVP House", "Tally BLMA", "Tally 2K23", "Tally FAMU FSU"],
                "Discord": ["Main Server", "Development Server", "Test Server", "Community Server"],
                "Telegram": ["Main Group", "Support Group", "Announcements", "VIP Group"],
                "Signal": ["Phone 1", "Phone 2", "Backup Phone", "Emergency Line"]
            }

            # Bot types for assignment
            bot_types = [
                "moderator", "administrator", "support", "entertainment",
                "information", "automation", "analytics", "custom"
            ]

            # Bot-Channel Assignment Grid
            for bot in state.bots:
                with ui.card().classes("p-4 border border-gray-200"):
                    ui.label(f"🤖 {bot.bot_name} - Channel Assignments").classes("text-sm font-semibold")

                    # Current assignments summary with types
                    current_assignments = _get_bot_channel_assignments(bot.bot_name)
                    if current_assignments:
                        with ui.row().classes("gap-2 mb-3 flex-wrap"):
                            for platform, channel_assignments in current_assignments.items():
                                for channel_data in channel_assignments:
                                    channel = channel_data["channel"]
                                    bot_type = channel_data["type"]
                                    ui.chip(f"{platform}: {channel} ({bot_type})").classes("bg-purple-100 text-purple-700 text-xs")
                    else:
                        ui.label("No channels assigned").classes("text-xs text-gray-500 mb-3")

                    # Assignment controls by platform
                    for platform, channels in available_channels.items():
                        with ui.column().classes("gap-2 mb-3"):
                            ui.label(f"{platform} Channels").classes("text-xs font-medium text-gray-600 uppercase")

                            # Create assignment forms for each channel
                            for channel in channels:
                                current_assignment = _get_bot_channel_assignment(bot.bot_name, channel, platform)
                                if current_assignment:
                                    # Show current assignment with edit option
                                    with ui.row().classes("items-center gap-2 w-full"):
                                        ui.label(f"Currently: {current_assignment['type']}").classes("text-sm flex-1")
                                        ui.button("Edit", on_click=lambda b=bot.bot_name, c=channel, p=platform:
                                                 _show_channel_assignment_dialog(b, c, p, bot_types, on_status_change)).props("size=sm")
                                        ui.button("Remove", on_click=lambda b=bot.bot_name, c=channel, p=platform:
                                                 _remove_channel_assignment(b, c, p, on_status_change)).props("size=sm color=warning")
                                else:
                                    # Show assign button
                                    with ui.row().classes("gap-2 w-full"):
                                        ui.button(f"Assign to {channel}",
                                                 on_click=lambda b=bot.bot_name, c=channel, p=platform:
                                                 _show_channel_assignment_dialog(b, c, p, bot_types, on_status_change)).props("size=sm color=primary")
                                        ui.label("Not assigned").classes("text-xs text-gray-500")

            # Quick assignment buttons
            with ui.card().classes("p-4 border border-gray-200 mt-4"):
                ui.label("Quick Assignment Tools").classes("text-sm font-semibold mb-3")

                with ui.row().classes("gap-2 flex-wrap"):
                    ui.button("Assign All to Main Channels",
                             on_click=lambda: _assign_all_to_main_channels(state, on_status_change)).props("size=sm color=primary")
                    ui.button("Clear All Assignments",
                             on_click=lambda: _clear_all_assignments(state, on_status_change)).props("size=sm color=warning")
                    ui.button("Auto-assign by Bot Type ■",
                             on_click=lambda: _auto_assign_by_bot_type(state, on_status_change)).props("size=sm color=info")

                for bot in state.bots:
                    active = controller.get_status(bot.bot_name)
                    with ui.row().classes(
                        "items-center justify-between gap-4 w-full bg-gray-50 border border-gray-100 rounded-lg px-3 py-2"
                    ):
                        with ui.column().classes("gap-1"):
                            ui.label(bot.bot_name).classes("text-sm font-medium")
                            status_label = ui.label("").classes("text-xs text-gray-500")
                            status_label.set_text(
                                f"Automation status: {'Active' if active else 'Paused'}"
                            )

                        # Enhanced controls for active bots and admins
                        with ui.row().classes("gap-2"):
                            if active:
                                # Bot is active - show pause and stop controls for admins
                                if state.role == Role.ADMIN:
                                    ui.button("⏸️ Pause", on_click=lambda b=bot.bot_name: _pause_bot(b, controller, state)).props("size=sm color=warning")
                                    ui.button("⏹️ Stop", on_click=lambda b=bot.bot_name: _stop_bot(b, controller, state)).props("size=sm color=negative")
                                else:
                                    ui.label("Active").classes("text-xs bg-green-100 text-green-700 px-2 py-1 rounded")
                            else:
                                # Bot is paused - show play control for admins
                                if state.role == Role.ADMIN:
                                    ui.button("▶️ Play", on_click=lambda b=bot.bot_name: _play_bot(b, controller, state)).props("size=sm color=positive")
                                else:
                                    ui.label("Paused").classes("text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded")

                    def handle_change(event, name=bot.bot_name) -> None:
                        state.toggle_bot(name, bool(event.value))
                        on_status_change()

                    def handle_status_update(active: bool, name=bot.bot_name, label=status_label) -> None:
                        label.set_text(f"Automation status: {'Active' if active else 'Paused'}")
                        on_status_change()

                    controller.subscribe_status(bot.bot_name, handle_status_update)


def _is_bot_assigned_to_channel(bot_name: str, channel: str, platform: str) -> bool:
    """Check if a bot is assigned to a specific channel."""
    # This would typically check a database or configuration
    # For now, return True for some bots as examples
    assignment_examples = {
        ("Zort Pro", "Tally Main", "GroupMe"): True,
        ("Zort Pro", "Tally Subleasing", "GroupMe"): True,
        ("Zort Pro", "Main Server", "Discord"): True,
    }
    return assignment_examples.get((bot_name, channel, platform), False)


def _pause_bot(bot_name: str, controller: BotController, state: DashboardState) -> None:
    """Pause a running bot."""
    print(f"Pausing bot: {bot_name}")
    controller.pause_bot(bot_name)
    state.toggle_bot(bot_name, False)
    ui.notify(f"Bot '{bot_name}' paused", color="orange")


def _stop_bot(bot_name: str, controller: BotController, state: DashboardState) -> None:
    """Stop a running bot completely."""
    print(f"Stopping bot: {bot_name}")
    controller.stop_bot(bot_name)
    state.toggle_bot(bot_name, False)
    ui.notify(f"Bot '{bot_name}' stopped", color="red")


def _play_bot(bot_name: str, controller: BotController, state: DashboardState) -> None:
    """Resume a paused bot."""
    print(f"Resuming bot: {bot_name}")
    controller.resume_bot(bot_name)
    state.toggle_bot(bot_name, True)
    ui.notify(f"Bot '{bot_name}' resumed", color="green")


def _render_bot_assistant_connections(state: DashboardState, controller: BotController) -> None:
    """Render bot-AI assistant connection management."""

    with ui.expansion("Bot-AI Assistant Connections", value=False).classes(
        "rounded-lg border border-gray-100 mt-4"
    ):
        with ui.column().classes("gap-4 w-full"):
            ui.label("Connect Bots with AI Assistants").classes("text-sm font-medium")

            # Mock AI assistants data - in real app this would come from backend
            available_assistants = [
                {"id": "1", "title": "Customer Support Bot", "description": "Handles customer inquiries"},
                {"id": "2", "title": "Sales Assistant", "description": "Helps with sales questions"},
                {"id": "3", "title": "Technical Support", "description": "Provides technical assistance"},
                {"id": "4", "title": "Content Moderator", "description": "Moderates conversations"},
                {"id": "5", "title": "Analytics Assistant", "description": "Provides insights and reports"},
            ]

            if not available_assistants:
                ui.label("No AI assistants available. Create one first in the AI Assistants tab.").classes("text-sm text-gray-500")
                return

            # Bot-Assistant Connection Grid
            for bot in state.bots:
                with ui.card().classes("p-4 border border-gray-200"):
                    ui.label(f"{bot.bot_name} - AI Assistant Connections").classes("text-sm font-semibold")

                    # Current connections display
                    current_connections = _get_bot_assistant_connections(bot.bot_name)
                    if current_connections:
                        with ui.row().classes("gap-2 mb-3 flex-wrap"):
                            for assistant_id in current_connections:
                                assistant = next((a for a in available_assistants if a["id"] == assistant_id), None)
                                if assistant:
                                    ui.chip(f"🔗 {assistant['title']}").classes("bg-blue-100 text-blue-700 text-xs")
                    else:
                        ui.label("No AI assistants connected").classes("text-xs text-gray-500 mb-3")

                    # Connection controls
                    with ui.row().classes("gap-2 w-full"):
                        assistant_select = ui.select(
                            {a["id"]: f"{a['title']} - {a['description']}" for a in available_assistants},
                            value=None,
                            label="Connect AI Assistant"
                        ).classes("flex-1")

                        def connect_assistant(bot_name=bot.bot_name):
                            if assistant_select.value:
                                _connect_bot_to_assistant(bot_name, assistant_select.value)
                                ui.notify(f"Connected '{bot_name}' to AI assistant", color="green")
                                # Refresh would happen here in real implementation

                        def disconnect_all(bot_name=bot.bot_name):
                            _disconnect_all_assistants(bot_name)
                            ui.notify(f"Disconnected all AI assistants from '{bot_name}'", color="orange")

                        ui.button("Connect", on_click=connect_assistant).props("size=sm color=positive")
                        if current_connections:
                            ui.button("Disconnect All", on_click=disconnect_all).props("size=sm color=warning")


def _get_bot_assistant_connections(bot_name: str) -> list:
    """Get list of AI assistant IDs connected to a bot."""
    # Mock data - in real app this would query the database
    connections = {
        "Zort Pro": ["1", "2"],  # Connected to Customer Support and Sales Assistant
        "Bot 2": ["3"],  # Connected to Technical Support
        "Bot 3": ["4", "5"],  # Connected to Content Moderator and Analytics Assistant
        "Bot 4": [],  # No connections yet
    }
    return connections.get(bot_name, [])


def _connect_bot_to_assistant(bot_name: str, assistant_id: str) -> None:
    """Connect a bot to an AI assistant."""
    print(f"Connecting bot '{bot_name}' to AI assistant '{assistant_id}'")
    # Here you would save this connection to your backend/database


def _disconnect_all_assistants(bot_name: str) -> None:
    """Disconnect all AI assistants from a bot."""
    print(f"Disconnecting all AI assistants from bot '{bot_name}'")
    # Here you would remove all connections for this bot


def _assign_all_to_main_channels(state: DashboardState, on_status_change: Callable[[], None]) -> None:
    """Assign all bots to their main channels."""
    main_channels = {
        "GroupMe": ["Tally Main"],
        "Discord": ["Main Server"],
        "Telegram": ["Main Group"],
        "Signal": ["Phone 1"]
    }

    for bot in state.bots:
        for platform, channels in main_channels.items():
            for channel in channels:
                _update_bot_channel_assignment(bot.bot_name, channel, platform, True)

    ui.notify("All bots assigned to main channels", color="green")
    on_status_change()


def _clear_all_assignments(state: DashboardState, on_status_change: Callable[[], None]) -> None:
    """Clear all bot channel assignments."""
    for bot in state.bots:
        # Clear all assignments for this bot
        _clear_bot_assignments(bot.bot_name)

    ui.notify("All bot assignments cleared", color="orange")
    on_status_change()


def _auto_assign_by_bot_type(state: DashboardState, on_status_change: Callable[[], None]) -> None:
    """Auto-assign bots to channels based on their type/capabilities."""
    # This would be more sophisticated in a real implementation
    # For now, just assign based on bot names
    for bot in state.bots:
        if "Zort" in bot.bot_name:
            _update_bot_channel_assignment(bot.bot_name, "Tally Main", "GroupMe", True)
            _update_bot_channel_assignment(bot.bot_name, "Main Server", "Discord", True)
        elif "Support" in bot.bot_name:
            _update_bot_channel_assignment(bot.bot_name, "Support Group", "Telegram", True)
        elif "Moderator" in bot.bot_name:
            _update_bot_channel_assignment(bot.bot_name, "Tally Main", "GroupMe", True)

    ui.notify("Bots auto-assigned by type", color="blue")
    on_status_change()


def _clear_bot_assignments(bot_name: str) -> None:
    """Clear all channel assignments for a specific bot."""
    print(f"Clearing all assignments for bot: {bot_name}")
    # Here you would clear all assignments for this bot in the backend


def _get_bot_channel_assignments(bot_name: str) -> dict:
    """Get current channel assignments for a bot."""
    # Mock data - in real app this would query the database
    assignments = {
        "Zort Pro": {
            "GroupMe": [{"channel": "Tally Main", "type": "moderator"}, {"channel": "Tally Subleasing", "type": "information"}],
            "Discord": [{"channel": "Main Server", "type": "administrator"}]
        },
        "Bot 2": {
            "Telegram": [{"channel": "Support Group", "type": "support"}]
        },
        "Bot 3": {
            "GroupMe": [{"channel": "Tally Main", "type": "entertainment"}],
            "Signal": [{"channel": "Phone 1", "type": "information"}]
        }
    }
    return assignments.get(bot_name, {})


def _get_bot_channel_assignment(bot_name: str, channel: str, platform: str) -> dict:
    """Get specific channel assignment for a bot."""
    assignments = _get_bot_channel_assignments(bot_name)
    platform_assignments = assignments.get(platform, [])
    for assignment in platform_assignments:
        if assignment["channel"] == channel:
            return assignment
    return {}


def _show_channel_assignment_dialog(bot_name: str, channel: str, platform: str, bot_types: list, on_status_change: Callable[[], None]) -> None:
    """Show dialog for assigning bot to channel with type selection."""

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-md"):
        ui.label(f"Assign {bot_name} to {platform}: {channel}").classes("text-lg font-semibold mb-4")

        # Bot type selection
        type_select = ui.select(
            bot_types,
            value=bot_types[0] if bot_types else None,
            label="Bot Type"
        ).classes("w-full mb-4")

        with ui.row().classes("gap-2 mt-4"):
            def assign_bot():
                if type_select.value:
                    _update_bot_channel_assignment(bot_name, channel, platform, type_select.value, True)
                    ui.notify(f"Assigned '{bot_name}' as {type_select.value} to {platform}: {channel}", color="green")
                    on_status_change()
                    dialog.close()

            def cancel():
                dialog.close()

            ui.button("Assign", on_click=assign_bot).props("color=primary")
            ui.button("Cancel", on_click=cancel).props("color=grey")


def _remove_channel_assignment(bot_name: str, channel: str, platform: str, on_status_change: Callable[[], None]) -> None:
    """Remove bot from channel assignment."""
    _update_bot_channel_assignment(bot_name, channel, platform, "", False)
    ui.notify(f"Removed '{bot_name}' from {platform}: {channel}", color="orange")
    on_status_change()


def _update_bot_channel_assignment(bot_name: str, channel: str, platform: str, bot_type: str = "", assigned: bool = True) -> None:
    """Update bot-channel assignment in the backend."""
    # This would typically update a database or send to backend API
    if assigned:
        print(f"Bot '{bot_name}' assigned to '{channel}' on {platform} as {bot_type}")
    else:
        print(f"Bot '{bot_name}' removed from '{channel}' on {platform}")
    # Here you would save this assignment to your backend/database
