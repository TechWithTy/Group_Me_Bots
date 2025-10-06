#!/usr/bin/env python3
"""
Main entry point for GroupMint Telegram Bot and Workflows.
Runs the API server and bot concurrently for testing.
"""

import asyncio
import logging
import uvicorn
from multiprocessing import Process

# Import our components
from app.telegram.main import app as api_app
from app.telegram.bots.enhanced_bot import application as bot_app

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_api_server():
    """Run the FastAPI server in a separate process."""
    uvicorn.run(api_app, host="localhost", port=8000, log_level="info")

async def run_bot():
    """Run the Telegram bot."""
    logger.info("Starting Telegram bot...")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.idle()

async def main():
    """Main function to run API and bot concurrently."""
    logger.info("Starting GroupMint system...")

    # Run API server in a separate process
    api_process = Process(target=run_api_server)
    api_process.start()

    # Wait a bit for API to start
    await asyncio.sleep(2)

    # Run bot in the main process
    try:
        await run_bot()
    finally:
        api_process.terminate()
        api_process.join()

if __name__ == "__main__":
    asyncio.run(main())
