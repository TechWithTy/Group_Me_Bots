"""
Main API router for Telegram endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter

# Import routers to avoid circular imports
def get_api_router() -> APIRouter:
    """Get the main API router with all endpoints included."""
    router = APIRouter()

    # Lazy import to avoid circular imports
    from app.telegram.api import auth, products, cart, orders, payments, analytics

    # Include endpoint routers
    router.include_router(
        auth.router,
        prefix="/telegram/auth",
        tags=["authentication"]
    )

    router.include_router(
        products.router,
        prefix="/telegram/products",
        tags=["products"]
    )

    router.include_router(
        cart.router,
        prefix="/telegram/cart",
        tags=["cart"]
    )

    router.include_router(
        orders.router,
        prefix="/telegram/orders",
        tags=["orders"]
    )

    router.include_router(
        payments.router,
        prefix="/telegram/payments",
        tags=["payments"]
    )

    router.include_router(
        analytics.router,
        prefix="/telegram/analytics",
        tags=["analytics"]
    )

    return router


# Create router instance
router = get_api_router()
