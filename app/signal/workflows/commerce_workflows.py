"""Commerce-oriented workflows leveraging Signal-specific messaging flows."""
from __future__ import annotations

from typing import Any

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = ["SignalCommerceEscrowWorkflow"]


class SignalCommerceEscrowWorkflow(WorkflowDefinition):
    """Coordinate escrow releases and confirmations through Signal chats."""

    name = "signal_commerce_escrow"
    title = "Signal Commerce Escrow"
    description = (
        "Creates Signal-native payment confirmations, tracks escrow states, and "
        "releases funds once buyers acknowledge delivery via secure messaging."
    )
    goal = "Guarantee timely escrow releases for verified Signal commerce orders."
    kpis = (
        WorkflowKPI("invoice_conversion", "100%", "Orders converted into invoices"),
        WorkflowKPI("escrow_release_rate", "100%", "Invoices released from escrow"),
        WorkflowKPI("confirmation_latency", "<2h", "Latency between confirmation and release"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        payments_client = self._require(context, "payments_client")

        orders: tuple[dict[str, Any], ...] = tuple(kwargs.get("orders", ()))
        auto_release: bool = bool(kwargs.get("auto_release", False))
        currency: str = kwargs.get("currency", "USD")

        if not orders:
            return WorkflowResult(False, {"error": "orders are required"})

        invoices_created = 0
        escrow_released = 0

        for order in orders:
            invoice = await payments_client.create_invoice(
                order_id=order.get("order_id"),
                amount=order.get("amount", 0.0),
                currency=currency,
                platform="signal",
                metadata={"buyer": order.get("buyer"), "seller": order.get("seller")},
            )
            invoices_created += 1 if invoice else 0

            should_release = auto_release or order.get("release_on_confirmation", False)
            if should_release:
                await payments_client.release_escrow(
                    order_id=order.get("order_id"),
                    amount=order.get("amount", 0.0),
                    currency=currency,
                )
                escrow_released += 1

        order_count = len(orders)
        achieved = invoices_created == order_count and (
            not auto_release or escrow_released == invoices_created
        )

        metrics = {
            "orders_processed": order_count,
            "invoices_created": invoices_created,
            "escrow_released": escrow_released,
            "currency": currency,
            "auto_release": auto_release,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)
