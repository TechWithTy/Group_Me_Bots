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
        with ui.column().classes("gap-4"):
            ui.label("AI Assistants").classes("text-lg font-semibold")
            ui.label(
                "Monitor active assistants, their specialties, and supported workflows."
            ).classes("text-sm text-gray-600")

            # Create New Assistant Section
            _render_create_assistant_form()

            # Existing Assistants Overview
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


def _render_create_assistant_form() -> None:
    """Render form to create new AI assistants."""

    # Define variables in outer scope for access in nested functions
    title_input = None
    description_input = None
    avatar_url_input = None
    prompt_input = None
    model_select = None
    provider_select = None
    temperature_input = None
    top_p_input = None
    max_tokens_input = None
    frequency_penalty_input = None
    presence_penalty_input = None

    def create_assistant():
        # Validate required fields
        if not title_input.value:
            ui.notify("Assistant title is required", color="red")
            return

        # Create assistant data
        assistant_data = {
            "title": title_input.value,
            "description": description_input.value,
            "avatar_url": avatar_url_input.value or "",
            "prompt": prompt_input.value,
            "model": model_select.value,
            "provider": provider_select.value,
            "temperature": temperature_input.value,
            "top_p": top_p_input.value,
            "max_tokens": max_tokens_input.value,
            "frequency_penalty": frequency_penalty_input.value,
            "presence_penalty": presence_penalty_input.value,
            "created_at": ui.query("new Date().toISOString()")
        }

        # Here you would typically save to database or send to backend
        print(f"Created assistant: {assistant_data}")
        ui.notify(f"Assistant '{title_input.value}' created successfully!", color="green")

        # Reset form
        title_input.set_value("")
        description_input.set_value("")
        avatar_url_input.set_value("")
        prompt_input.set_value("")

    with ui.expansion("Create New AI Assistant", value=False).classes(
        "rounded-lg border border-gray-100"
    ):
        with ui.column().classes("gap-4 w-full"):
            ui.label("Configure your new AI assistant").classes("text-sm font-medium text-gray-700")

            # Basic Information
            with ui.row().classes("gap-4 w-full"):
                with ui.column().classes("flex-1 gap-2"):
                    ui.label("Basic Information").classes("text-xs font-semibold text-gray-600 uppercase")
                    title_input = ui.input("Assistant Title",
                                         placeholder="e.g. Customer Support Bot",
                                         validation={"Required": lambda x: len(x) > 0}).classes("w-full")
                    description_input = ui.textarea("Description",
                                                   placeholder="Describe what this assistant does...").classes("w-full")

            # Model and Provider Selection
            with ui.row().classes("gap-4 w-full"):
                with ui.column().classes("flex-1 gap-2"):
                    ui.label("AI Model & Provider").classes("text-xs font-semibold text-gray-600 uppercase")

                    # Provider selection
                    provider_select = ui.select(
                        ["openrouter", "openai", "anthropic", "google", "local"],
                        value="openrouter",
                        label="AI Provider"
                    ).classes("w-full")

                    # Model selection based on provider
                    model_select = ui.select(
                        [
                            "anthropic/claude-3.5-sonnet",
                            "anthropic/claude-3-haiku",
                            "openai/gpt-4",
                            "openai/gpt-3.5-turbo",
                            "google/gemini-pro",
                            "meta-llama/llama-3.1-70b-instruct",
                            "mistralai/mixtral-8x7b-instruct"
                        ],
                        value="anthropic/claude-3.5-sonnet",
                        label="AI Model"
                    ).classes("w-full")

            # Avatar and Prompt
            with ui.row().classes("gap-4 w-full"):
                with ui.column().classes("flex-1 gap-2"):
                    ui.label("Avatar & Behavior").classes("text-xs font-semibold text-gray-600 uppercase")

                    # Avatar upload section
                    with ui.card().classes("p-3 border border-gray-200"):
                        ui.label("Avatar Image").classes("text-sm font-medium")
                        avatar_upload = ui.upload(
                            label="Upload Avatar",
                            auto_upload=True,
                            max_files=1,
                            max_file_size=5*1024*1024  # 5MB
                        ).classes("w-full")

                        avatar_url_input = ui.input("Or use URL",
                                                  placeholder="https://example.com/avatar.png").classes("w-full")

                        # Preview uploaded image
                        avatar_preview = ui.image().classes("w-16 h-16 rounded-lg object-cover mt-2")

                        def handle_avatar_upload(file_info):
                            if file_info:
                                avatar_preview.set_source(f"data:{file_info.type};base64,{file_info.content}")
                                avatar_url_input.set_value("")  # Clear URL input when file uploaded

                        avatar_upload.on_upload(handle_avatar_upload)

                    prompt_input = ui.textarea("System Prompt",
                                             placeholder="You are a helpful assistant that...").classes("w-full")

            # Advanced LLM Settings
            with ui.expansion("Advanced LLM Settings", value=False).classes(
                "rounded-lg border border-gray-100 mt-4"
            ):
                with ui.column().classes("gap-4 w-full"):
                    ui.label("Fine-tune your AI assistant's behavior").classes("text-sm font-medium text-gray-700")

                    # Basic settings
                    with ui.row().classes("gap-4 w-full"):
                        temperature_input = ui.number(
                            "Temperature",
                            value=0.7,
                            min=0.0,
                            max=2.0,
                            step=0.1,
                            format="%.1f"
                        ).classes("flex-1")

                        top_p_input = ui.number(
                            "Top P",
                            value=1.0,
                            min=0.0,
                            max=1.0,
                            step=0.05,
                            format="%.2f"
                        ).classes("flex-1")

                        max_tokens_input = ui.number(
                            "Max Tokens",
                            value=1000,
                            min=100,
                            max=4000,
                            step=100
                        ).classes("flex-1")

                    # Advanced settings
                    with ui.row().classes("gap-4 w-full"):
                        frequency_penalty_input = ui.number(
                            "Frequency Penalty",
                            value=0.0,
                            min=-2.0,
                            max=2.0,
                            step=0.1,
                            format="%.1f"
                        ).classes("flex-1")

                        presence_penalty_input = ui.number(
                            "Presence Penalty",
                            value=0.0,
                            min=-2.0,
                            max=2.0,
                            step=0.1,
                            format="%.1f"
                        ).classes("flex-1")

                    # Tooltips for settings
                    with ui.row().classes("gap-2 w-full text-xs text-gray-500"):
                        ui.label("Temperature: Controls randomness (0.0 = deterministic, 2.0 = very random)").classes("flex-1")
                        ui.label("Top P: Nucleus sampling (0.1 = focused, 1.0 = diverse)").classes("flex-1")
                        ui.label("Max Tokens: Maximum response length").classes("flex-1")

                    with ui.row().classes("gap-2 w-full text-xs text-gray-500"):
                        ui.label("Frequency Penalty: Reduces repetition of words (-2.0 to 2.0)").classes("flex-1")
                        ui.label("Presence Penalty: Reduces repetition of topics (-2.0 to 2.0)").classes("flex-1")

            # Action Buttons
            with ui.row().classes("gap-2 mt-4"):
                ui.button("Create Assistant", on_click=create_assistant).props("color=primary")
                ui.button("Reset Form", on_click=lambda: (
                    title_input.set_value(""),
                    description_input.set_value(""),
                    avatar_url_input.set_value(""),
                    prompt_input.set_value("")
                )).props("color=grey")


def _update_selected_servers(selected: bool, server_name: str, selected_servers: list) -> None:
    """Update the list of selected MCP servers."""
    if selected:
        if server_name not in selected_servers:
            selected_servers.append(server_name)
    else:
        if server_name in selected_servers:
            selected_servers.remove(server_name)
