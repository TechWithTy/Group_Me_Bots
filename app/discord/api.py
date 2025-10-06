"""FastAPI application for Discord API integrations."""
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .modules import (
    applications,
    channels,
    gateway,
    guilds,
    interactions,
    invites,
    messages,
    oauth2,
    users,
    voice,
    webhooks,
)
from .modules.core import DiscordAPIError, format_discord_error

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Discord API",
    description="API for Discord bot operations using discord.py",
    version="1.0.0",
)

for router in [
    applications.router,
    channels.router,
    guilds.router,
    users.router,
    messages.router,
    webhooks.router,
    voice.router,
    invites.router,
    interactions.router,
    gateway.router,
    oauth2.router,
]:
    app.include_router(router)


@app.exception_handler(DiscordAPIError)
async def discord_api_error_handler(_, exc: DiscordAPIError):
    """Handle DiscordAPIError exceptions and format the response."""
    return JSONResponse(status_code=exc.status_code, content=format_discord_error(exc))


@app.get("/")
async def root() -> dict:
    """Root endpoint to verify service availability."""
    return {"message": "Discord API is running"}
