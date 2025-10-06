#!/usr/bin/env python3
"""
Test script for GroupMint Telegram Bot and Workflows.
Tests API endpoints and bot integration.
"""

import asyncio
import httpx
import logging

# Import our components
from app.telegram.workflows.orchestrator import run_daily_analytics, background_order_check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000/api/v1/telegram"

async def test_api_endpoints():
    """Test the API endpoints."""
    logger.info("Testing API endpoints...")

    async with httpx.AsyncClient() as client:
        # Test products endpoint
        try:
            response = await client.get(f"{API_BASE_URL}/products")
            if response.status_code == 200:
                logger.info("✅ Products endpoint working")
            else:
                logger.error(f"❌ Products endpoint failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Products endpoint error: {e}")

        # Test auth endpoint (mock user)
        try:
            response = await client.post(f"{API_BASE_URL}/auth/telegram", json={
                "telegram_id": "123456789",
                "username": "test_user",
                "first_name": "Test",
                "last_name": "User"
            })
            if response.status_code == 200:
                logger.info("✅ Auth endpoint working")
            else:
                logger.error(f"❌ Auth endpoint failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Auth endpoint error: {e}")

async def test_workflows():
    """Test the workflows."""
    logger.info("Testing workflows...")

    try:
        # Test analytics workflow
        result = await run_daily_analytics()
        if result:
            logger.info("✅ Analytics workflow working")
        else:
            logger.error("❌ Analytics workflow failed")
    except Exception as e:
        logger.error(f"❌ Analytics workflow error: {e}")

    try:
        # Test background task
        await background_order_check()
        logger.info("✅ Background order check working")
    except Exception as e:
        logger.error(f"❌ Background order check error: {e}")

async def main():
    """Run all tests."""
    logger.info("Starting GroupMint tests...")

    # Wait for API server to start (assuming it's running)
    await asyncio.sleep(2)

    await test_api_endpoints()
    await test_workflows()

    logger.info("Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
