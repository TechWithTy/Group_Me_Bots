"""
Analytics Workflow for GroupMint.
Handles tracking and reporting analytics events.
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

async def track_user_action(update: Update, action: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Track user actions for analytics."""
    user_id = str(update.effective_user.id)
    event_data = {
        "event": action,
        "user_id": user_id,
        "chat_id": update.effective_chat.id,
        "timestamp": asyncio.get_event_loop().time()
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{API_BASE_URL}/analytics/events", json=event_data)
        except Exception as e:
            logger.error(f"Error tracking event: {e}")

async def get_analytics_overview() -> Dict[str, Any]:
    """Fetch analytics overview."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/analytics/overview")
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching analytics: {e}")
            return {"status": "error", "message": str(e)}

async def generate_sales_report() -> Dict[str, Any]:
    """Generate sales report."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/analytics/reports/sales")
            return response.json()
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {"status": "error", "message": str(e)}
