"""Activity log rendering."""

from __future__ import annotations

from typing import List

from nicegui import ui

from ..state import DashboardState


def render_activity_log(state: DashboardState) -> None:
    """Render the latest activity feed."""

    with ui.card().classes("w-full border border-gray-200 shadow-sm"):
        ui.label("Recent Activity").classes("text-lg font-semibold")
        ui.label("Latest configuration changes across the workspace.").classes(
            "text-sm text-gray-600"
        )
        container = ui.column().classes("gap-2 mt-3")

    def update(entries: List[str]) -> None:
        container.clear()
        if not entries:
            with container:
                ui.label("No activity yet.").classes("text-sm text-gray-500")
            return
        for entry in entries:
            with container:
                ui.label(entry).classes(
                    "text-sm bg-gray-50 border border-gray-100 rounded-md px-3 py-2"
                )

    state.subscribe_activity(update)
