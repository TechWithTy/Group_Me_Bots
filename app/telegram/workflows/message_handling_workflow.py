"""
Message Handling Workflow for Telegram Bot.

This workflow handles incoming messages and provides automated responses
using existing Telegram API endpoints.
"""

import time
from typing import Dict, Any, List, Optional
from app.telegram.api.telegram_api import TelegramBotAPI, Update, Message


class MessageHandlingWorkflow:
    """Workflow for processing and responding to messages."""

    title = "Telegram Message Handling"
    description = "Route inbound Telegram messages to the right command handlers with contextual replies."
    goal = "Respond to recognized commands and keywords with actionable guidance within seconds."
    kpis = [
        {
            "name": "commands_handled",
            "target": ">=90%",
            "description": "Percentage of recognized commands receiving an automated response.",
        },
        {
            "name": "average_response_latency",
            "target": "<3s",
            "description": "Average time taken to send a response after receiving a message.",
        },
        {
            "name": "fallback_rate",
            "target": "<10%",
            "description": "Share of messages that route to the default handler due to no match.",
        },
    ]

    def __init__(self, bot: TelegramBotAPI):
        self.bot = bot
        self.handlers = {
            '/start': self.handle_start,
            '/help': self.handle_help,
            '/status': self.handle_status,
        }

    def process_update(self, update: Update) -> None:
        """Process an incoming update."""
        if update.message:
            self.process_message(update.message)

    def process_message(self, message: Message) -> None:
        """Process a single message."""
        if message.text:
            self.handle_text_message(message)

    def handle_text_message(self, message: Message) -> None:
        """Handle text messages based on commands."""
        text = message.text.strip()
        if text in self.handlers:
            self.handlers[text](message)
        else:
            self.handle_default(message)

    def handle_start(self, message: Message) -> None:
        """Handle /start command."""
        response = "Welcome to the bot! Use /help for commands."
        self.bot.send_message(message.chat.id, response)

    def handle_help(self, message: Message) -> None:
        """Handle /help command."""
        help_text = """
Available commands:
- /start: Start the bot
- /help: Show this help
- /status: Check bot status
        """
        self.bot.send_message(message.chat.id, help_text.strip())

    def handle_status(self, message: Message) -> None:
        """Handle /status command."""
        status = "Bot is running and ready to process messages."
        self.bot.send_message(message.chat.id, status)

    def handle_default(self, message: Message) -> None:
        """Handle unknown messages."""
        response = "I don't understand that command. Use /help for available options."
        self.bot.send_message(message.chat.id, response)

    def echo_message(self, message: Message) -> None:
        """Echo the message back (example response)."""
        if message.text:
            self.bot.send_message(message.chat.id, f"You said: {message.text}")

    def check_for_keywords(self, message: Message) -> None:
        """Check for specific keywords and respond."""
        if message.text and 'hello' in message.text.lower():
            self.bot.send_message(message.chat.id, "Hello there!")
        elif message.text and 'bye' in message.text.lower():
            self.bot.send_message(message.chat.id, "Goodbye!")

    def run_workflow(self, updates: List[Update]) -> None:
        """Run the workflow on a list of updates."""
        for update in updates:
            self.process_update(update)
            time.sleep(0.1)  # Small delay to avoid rate limits
