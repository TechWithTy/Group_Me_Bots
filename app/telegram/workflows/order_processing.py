"""
Order Processing Workflow for GroupMint.
Handles order creation, updates, and fulfillment.
"""

import asyncio
import logging
import httpx
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

# Import our components
from app.telegram.bots.enhanced_bot import API_BASE_URL

logger = logging.getLogger(__name__)

async def create_order_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    """Create an order from the user's cart."""
    user_id = str(update.effective_user.id)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/orders/create?user_id={user_id}")
            if response.status_code == 200:
                order_data = response.json()
                await update.message.reply_text(f"Order created! Order ID: {order_data.get('id')}")
                return {"status": "success", "order_id": order_data.get('id'), "data": order_data}
            else:
                await update.message.reply_text("Failed to create order. Please check your cart.")
                return {"status": "error", "message": response.text}
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            await update.message.reply_text("Error creating order.")
            return {"status": "error", "message": str(e)}

async def update_order_status(order_id: str, status: str) -> Dict[str, Any]:
    """Update order status (admin function)."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(f"{API_BASE_URL}/orders/{order_id}/status?status={status}")
            return response.json()
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return {"status": "error", "message": str(e)}

async def get_order_details(order_id: str) -> Dict[str, Any]:
    """Fetch order details."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/orders/{order_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching order details: {e}")
            return {"status": "error", "message": str(e)}
