"""Credits and billing overview."""

from __future__ import annotations

from nicegui import ui

from ..state import DashboardState


def render_credit_summary(state: DashboardState) -> None:
    """Render subscription status and purchase controls."""

    plan = state.plan
    subscription = state.subscription
    with ui.card().classes("w-full max-w-md"):
        ui.label("Credits & Billing").classes("text-lg font-semibold")
        ui.label(f"Plan: {plan.name} ({plan.tier.value})").classes("text-sm")
        ui.label(
            f"Renewal date: {subscription.current_period_end.date().isoformat()}"
        ).classes("text-sm text-gray-600")
        usage_label = ui.label(state.credit_summary()).classes("text-sm text-gray-600")
        ui.label(
            "Feature highlights: analytics, SSO, advanced moderation"
        ).classes("text-xs text-gray-500 mt-2")

        ui.label("Purchase add-on credits").classes("text-sm font-medium mt-4")
        selected = {"amount": 25}

        def set_selected(amount: int) -> None:
            selected["amount"] = amount
            selection_label.set_text(f"Selected package: {amount} credits")

        with ui.row().classes("gap-2 flex-wrap mt-2"):
            for amount in (10, 25, 50, 100):
                ui.button(
                    f"{amount} Credits (${amount})",
                    on_click=lambda a=amount: set_selected(a),
                )

        selection_label = ui.label("Selected package: 25 credits").classes(
            "text-xs text-gray-500"
        )
        status_label = ui.label("").classes("text-xs text-gray-500 mt-2")
        checkout_link = ui.link("", "#", new_tab=True).classes(
            "text-sm text-primary-500"
        )
        session_ref = {"id": None}

        def create_session() -> None:
            amount = selected["amount"]
            session_id, url = state.create_checkout_session(amount)
            session_ref["id"] = session_id
            status_label.set_text(f"Checkout ready for {amount} credits")
            checkout_link.set_text("Complete Purchase")
            checkout_link.set_href(url)
            confirm_button.enable()

        ui.button("Create checkout session", on_click=create_session).classes("mt-2")

        def confirm_payment() -> None:
            session_id = session_ref["id"]
            if not session_id:
                return
            try:
                amount = state.complete_checkout(session_id)
            except ValueError:
                status_label.set_text("Checkout session expired.")
                confirm_button.disable()
                return
            session_ref["id"] = None
            confirm_button.disable()
            status_label.set_text(
                f"Payment successful! {amount} credits added to your account."
            )

        confirm_button = ui.button("Confirm payment", on_click=confirm_payment).classes(
            "mt-2"
        )
        confirm_button.disable()

    def update_usage(used: int, limit: int, addon: int) -> None:
        summary = f"Credits used: {used} / {limit}"
        if addon:
            summary = f"{summary} | Add-on credits: {addon}"
        usage_label.set_text(summary)

    state.subscribe_credits(update_usage)
