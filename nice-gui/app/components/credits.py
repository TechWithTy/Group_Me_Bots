"""Credits and billing overview."""

from __future__ import annotations

from nicegui import ui

from ..state import DashboardState


def render_credit_summary(state: DashboardState) -> ui.label:
    """Render the current subscription and credit usage."""

    plan = state.plan
    subscription = state.subscription
    with ui.card().classes("w-full max-w-md"):
        ui.label("Credits & Billing").classes("text-lg font-semibold")
        ui.label(
            f"Plan: {plan.name} ({plan.tier.value})"
        ).classes("text-sm")
        ui.label(
            f"Renewal date: {subscription.current_period_end.date().isoformat()}"
        ).classes("text-sm text-gray-600")
        usage_label = ui.label(state.credit_summary()).classes("text-sm text-gray-600")
        ui.label(
            "Feature highlights: analytics, SSO, advanced moderation"
        ).classes("text-xs text-gray-500 mt-2")

    def update_usage(used: int, limit: int) -> None:
        usage_label.set_text(f"Credits used: {used} / {limit}")

    state.subscribe_credits(update_usage)
    return usage_label
