"""Reusable configuration section renderer."""

from __future__ import annotations

from typing import Sequence

from nicegui import ui

from ..models.configuration import ConfigurationSection


def render_configuration_sections(
    title: str,
    subtitle: str,
    sections: Sequence[ConfigurationSection],
) -> None:
    """Render grouped configuration values inside expandable sections."""

    if not sections:
        return

    with ui.card().classes("w-full max-w-4xl"):
        ui.label(title).classes("text-lg font-semibold")
        if subtitle:
            ui.label(subtitle).classes("text-sm text-gray-600")

        for section in sections:
            with ui.expansion(section.title, value=True).classes(
                "mt-3 border border-gray-200 dark:border-gray-800 rounded-xl"
            ):
                if section.description:
                    ui.label(section.description).classes(
                        "text-xs text-gray-500 mb-2"
                    )
                for key, value in section.items:
                    with ui.row().classes(
                        "justify-between items-start gap-3 py-1 border-b "
                        "border-gray-100 dark:border-gray-700 last:border-0"
                    ):
                        ui.label(key).classes(
                            "font-mono text-xs text-gray-500 break-all"
                        )
                        ui.label(value or "Not configured").classes(
                            "text-xs sm:text-sm text-gray-700 dark:text-gray-200 "
                            "text-right break-all"
                        )
