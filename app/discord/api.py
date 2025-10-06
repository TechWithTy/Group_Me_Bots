"""
Discord API module for Group_Me_Bots.

This module provides a FastAPI-based API that interfaces with Discord using discord.py.
It exposes endpoints for common Discord operations like channels, messages, and users.
"""
import os
import logging
from typing import List, Optional

import discord
from discord.ext import commands
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Discord API",
    description="API for Discord bot operations using discord.py",
    version="1.0.0"
)

# Discord bot setup
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is required")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# Pydantic models for API
class MessageRequest(BaseModel):
    """Request model for sending a message."""
    channel_id: int
    content: str

class ChannelRequest(BaseModel):
    """Request model for creating a channel."""
    guild_id: int
    name: str
    type: str = "text"

class DiscordChannel(BaseModel):
    """Response model for Discord channel."""
    id: int
    name: str
    type: str

class DiscordMessage(BaseModel):
    """Response model for Discord message."""
    id: int
    content: str
    author: str
    channel_id: int

# Dependency to get Discord client
async def get_discord_client():
    """Dependency to provide Discord bot client."""
    if not bot.is_ready():
        await bot.wait_until_ready()
    return bot

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Discord API is running"}

@app.get("/channels/{channel_id}", response_model=DiscordChannel)
async def get_channel(channel_id: int, client: commands.Bot = Depends(get_discord_client)):
    """Get channel information by ID."""
    try:
        channel = client.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        return DiscordChannel(id=channel.id, name=channel.name, type=str(channel.type))
    except Exception as e:
        logger.error(f"Error getting channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/channels", response_model=List[DiscordChannel])
async def list_channels(guild_id: int, client: commands.Bot = Depends(get_discord_client)):
    """List channels in a guild."""
    try:
        guild = client.get_guild(guild_id)
        if not guild:
            raise HTTPException(status_code=404, detail="Guild not found")
        channels = [DiscordChannel(id=c.id, name=c.name, type=str(c.type)) for c in guild.channels]
        return channels
    except Exception as e:
        logger.error(f"Error listing channels for guild {guild_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/messages", response_model=DiscordMessage)
async def send_message(request: MessageRequest, client: commands.Bot = Depends(get_discord_client)):
    """Send a message to a channel."""
    try:
        channel = client.get_channel(request.channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        message = await channel.send(request.content)
        return DiscordMessage(
            id=message.id,
            content=message.content,
            author=str(message.author),
            channel_id=message.channel.id
        )
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@app.get("/messages/{channel_id}", response_model=List[DiscordMessage])
async def get_messages(channel_id: int, limit: int = 10, client: commands.Bot = Depends(get_discord_client)):
    """Get recent messages from a channel."""
    try:
        channel = client.get_channel(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        messages = []
        async for message in channel.history(limit=limit):
            messages.append(DiscordMessage(
                id=message.id,
                content=message.content,
                author=str(message.author),
                channel_id=message.channel.id
            ))
        return messages
    except Exception as e:
        logger.error(f"Error getting messages for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    logger.info(f"Bot logged in as {bot.user}")

# Run the bot in the background (for development)
import asyncio

async def run_bot():
    """Run the Discord bot."""
    try:
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")

# Note: In production, run the bot separately or use a process manager
if __name__ == "__main__":
    # Start bot and server (for development only)
    import uvicorn
    # Run bot in background task would require proper async handling
    # For production, use separate processes
