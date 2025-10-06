"""
Core infrastructure for Discord API modules.

This module provides shared dependencies, error handling, and utilities
used across all Discord API endpoint modules.
"""
import os
import logging
from typing import Dict, Any, Optional

import discord
from discord.ext import commands
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Discord bot setup
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

# Initialize Discord bot with comprehensive intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Security scheme for OAuth2/Bot token authentication
security = HTTPBearer(auto_error=False)

# Rate limiting configuration (basic in-memory implementation)
# In production, use Redis or similar for distributed rate limiting
rate_limits: Dict[str, Dict[str, Any]] = {}

class DiscordAPIError(HTTPException):
    """Base exception for Discord API errors."""

    def __init__(self, status_code: int, detail: str, discord_code: Optional[int] = None):
        super().__init__(status_code=status_code, detail=detail)
        self.discord_code = discord_code

class RateLimitExceeded(DiscordAPIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, retry_after: float):
        super().__init__(
            status_code=429,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
            discord_code=40003
        )
        self.retry_after = retry_after

class ResourceNotFound(DiscordAPIError):
    """Exception raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=404,
            detail=f"{resource_type} with ID {resource_id} not found",
            discord_code=10062
        )

class InsufficientPermissions(DiscordAPIError):
    """Exception raised when user lacks required permissions."""

    def __init__(self, permission: str):
        super().__init__(
            status_code=403,
            detail=f"Insufficient permissions: {permission} required",
            discord_code=50013
        )

async def get_discord_client() -> commands.Bot:
    """Dependency to provide Discord bot client."""
    if not bot.is_ready():
        await bot.wait_until_ready()
    return bot

async def get_current_application(request: Request) -> str:
    """Extract and validate Discord application ID from request."""
    # This would typically come from the Authorization header or path parameter
    # For now, we'll use a default application ID
    # In production, this should validate against registered applications
    return "default_application"

async def validate_snowflake(snowflake_id: str) -> int:
    """Validate and convert snowflake ID to integer."""
    try:
        return int(snowflake_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid snowflake ID format")

def check_rate_limit(identifier: str, limit: int = 5, window: int = 60) -> None:
    """Basic rate limiting check."""
    import time

    current_time = time.time()
    if identifier not in rate_limits:
        rate_limits[identifier] = {"count": 1, "window_start": current_time}
        return

    user_limit = rate_limits[identifier]

    # Reset window if expired
    if current_time - user_limit["window_start"] > window:
        rate_limits[identifier] = {"count": 1, "window_start": current_time}
        return

    # Increment count
    user_limit["count"] += 1

    if user_limit["count"] > limit:
        retry_after = window - (current_time - user_limit["window_start"])
        raise RateLimitExceeded(retry_after)

def format_discord_error(error: Exception) -> dict:
    """Format Discord API errors consistently."""
    if isinstance(error, DiscordAPIError):
        return {
            "error": {
                "code": error.discord_code,
                "message": error.detail
            }
        }

    logger.error(f"Unexpected error: {error}")
    return {
        "error": {
            "code": 0,
            "message": "Internal server error"
        }
    }

# Bot event handlers
@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    logger.info(f"Bot logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_disconnect():
    """Event handler for when the bot disconnects."""
    logger.warning("Bot disconnected from Discord")

@bot.event
async def on_resumed():
    """Event handler for when the bot resumes connection."""
    logger.info("Bot resumed connection to Discord")

# Background task to run the bot
async def run_discord_bot():
    """Run the Discord bot in the background."""
    try:
        await bot.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token")
        raise
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")
        raise

# Cleanup function for graceful shutdown
async def cleanup():
    """Cleanup function for graceful shutdown."""
    if bot.is_ready():
        await bot.close()
    logger.info("Discord bot shut down gracefully")
