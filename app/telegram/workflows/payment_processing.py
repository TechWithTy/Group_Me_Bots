"""
Payment Workflow for GroupMint.
Handles payment processing, refunds, and status checks.
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

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float) -> Dict[str, Any]:
    """Process a payment via API."""
    user_id = str(update.effective_user.id)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/payments/create-invoice",
                json={"user_id": user_id, "amount": amount}
            )
            if response.status_code == 200:
                payment_data = response.json()
                await update.message.reply_text(f"Payment invoice created: {payment_data.get('invoice_url')}")
                return {"status": "success", "payment_id": payment_data.get('id'), "data": payment_data}
            else:
                await update.message.reply_text("Failed to create payment invoice.")
                return {"status": "error", "message": response.text}
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            await update.message.reply_text("Error processing payment.")
            return {"status": "error", "message": str(e)}

async def check_payment_status(payment_id: str) -> Dict[str, Any]:
    """Check payment status."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/payments/status/{payment_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return {"status": "error", "message": str(e)}

async def refund_payment(payment_id: str, reason: str = "Customer request") -> Dict[str, Any]:
    """Process a payment refund."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/payments/refund", json={"payment_id": payment_id, "reason": reason})
            return response.json()
        except Exception as e:
            logger.error(f"Error refunding payment: {e}")
            return {"status": "error", "message": str(e)}
