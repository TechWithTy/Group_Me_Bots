"""
User Registration Workflow for GroupMint.
Handles user onboarding via Telegram bot and API.
"""

import asyncio
import logging
import httpx
from typing import Dict, Any
from telegram import Update
from telegram.ext import ContextTypes

# Import our components
from app.telegram.bots.enhanced_bot import API_BASE_URL
from app.telegram.core.config import settings

logger = logging.getLogger(__name__)

async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
    """Register a new user via Telegram bot and API."""
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or f"user_{user_id}"

    user_data = {
        "telegram_id": user_id,
        "username": username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{API_BASE_URL}/auth/telegram", json=user_data)
            if response.status_code == 200:
                api_response = response.json()
                # Send welcome message via bot
                await update.message.reply_text(f"Welcome {user.first_name}! Registration successful.")
                return {"status": "success", "user_id": user_id, "data": api_response}
            else:
                await update.message.reply_text("Registration failed. Please try again.")
                return {"status": "error", "message": response.text}
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            await update.message.reply_text("Error during registration.")
            return {"status": "error", "message": str(e)}

async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Fetch user profile from API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/profile?user_id={user_id}")
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching profile: {e}")
            return {"status": "error", "message": str(e)}
