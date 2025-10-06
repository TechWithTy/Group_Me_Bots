# Telegram Workflows Suite

This directory contains a comprehensive suite of workflows for the GroupMint e-commerce platform, integrating Telegram bots, custom API endpoints, and the workers system.

## Workflows Overview

### 1. User Registration (`user_registration.py`)
- Handles user onboarding via Telegram bot
- Integrates with auth API for registration
- Tracks user profile data

### 2. Order Processing (`order_processing.py`)
- Manages order creation from cart
- Updates order statuses
- Fetches order details

### 3. Payment Processing (`payment_processing.py`)
- Processes payments via Telegram invoices
- Checks payment status
- Handles refunds

### 4. Notifications (`notifications.py`)
- Sends order confirmations
- Payment reminders
- Promotional messages

### 5. Analytics (`analytics.py`)
- Tracks user actions
- Fetches analytics data
- Generates reports

### 6. Orchestrator (`orchestrator.py`)
- Coordinates all workflows
- Provides high-level workflow functions
- Integrates with workers for background tasks

## Integration with Workers API

These workflows are designed to work with the existing workers system in the project. They use async functions that can be called as background tasks or job queue items.

## Usage

### Running Workflows via Bot
The workflows are triggered through the Telegram bots in `app/telegram/bots/`. For example:
- Use `/start` in the enhanced bot to trigger user onboarding
- Use `/checkout` to start order processing

### Background Tasks
Use the workers system to run workflows asynchronously:
```python
from app.telegram.workflows.orchestrator import run_daily_analytics

# Run as background task
asyncio.create_task(run_daily_analytics())
```

## Dependencies
- Telegram Bot API (`python-telegram-bot`)
- HTTP client (`httpx`) for API calls
- Async support for concurrency

## Configuration
Ensure your `.env` file includes:
- `TELEGRAM_BOT_TOKEN`
- API server host and port

## Next Steps
- Integrate with the main workers queue for automated task scheduling
- Add error handling and retry logic
- Implement webhook-based triggers for real-time processing
