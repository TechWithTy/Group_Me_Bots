"""
Message Stitching Workflow for Telegram Bot.

This workflow stitches multiple messages together based on context,
similar to GroupMe's MessageStitchingWorkflow.
"""

import time
import threading
from typing import Dict, Any, List
from collections import defaultdict
from app.telegram.api.telegram_api import TelegramBotAPI, Update, Message


class MessageStitchingWorkflow:
    """Workflow for stitching messages together based on patterns."""

    title = "Telegram Message Stitching"
    description = "Aggregate related Telegram messages into cohesive summaries for easier consumption."
    goal = "Combine contextual message sequences into stitched updates before notifying the chat."
    kpis = [
        {
            "name": "stitched_threads",
            "target": ">=1/run",
            "description": "Number of message groups successfully combined during processing.",
        },
        {
            "name": "average_stitch_size",
            "target": "3-5 messages",
            "description": "Average count of individual messages merged per stitched output.",
        },
        {
            "name": "stitch_success_rate",
            "target": ">=85%",
            "description": "Share of detected threads that produce a stitched message without errors.",
        },
    ]

    def __init__(self, bot: TelegramBotAPI, stitch_timeout: int = 300, max_stitch_length: int = 5):
        self.bot = bot
        self.stitch_timeout = stitch_timeout  # Seconds to wait before stitching
        self.max_stitch_length = max_stitch_length  # Max messages to stitch
        self.pending_messages = defaultdict(list)  # Chat ID -> list of messages
        self.stitch_timers = {}  # Chat ID -> timer

    def process_update(self, update: Update) -> None:
        """Process an incoming update for message stitching."""
        if update.message and update.message.text:
            self.add_message_to_stitch(update.message)

    def add_message_to_stitch(self, message: Message) -> None:
        """Add a message to the stitching queue."""
        chat_id = message.chat.id
        self.pending_messages[chat_id].append(message)

        # Check if we should stitch now
        if len(self.pending_messages[chat_id]) >= self.max_stitch_length:
            self.stitch_messages(chat_id)
        else:
            # Set or reset timer
            if chat_id in self.stitch_timers:
                self.stitch_timers[chat_id].cancel()
            self.stitch_timers[chat_id] = threading.Timer(self.stitch_timeout, self.stitch_messages, [chat_id])
            self.stitch_timers[chat_id].start()

    def stitch_messages(self, chat_id: int) -> None:
        """Stitch messages for a chat and send as one."""
        if chat_id not in self.pending_messages or not self.pending_messages[chat_id]:
            return

        messages = self.pending_messages[chat_id]
        if len(messages) > 1:
            stitched_text = self.create_stitched_text(messages)
            try:
                self.bot.send_message(chat_id, stitched_text)
            except Exception as e:
                print(f"Failed to send stitched message: {e}")

        # Clear pending messages and timer
        self.pending_messages[chat_id] = []
        if chat_id in self.stitch_timers:
            self.stitch_timers[chat_id].cancel()
            del self.stitch_timers[chat_id]

    def create_stitched_text(self, messages: List[Message]) -> str:
        """Create stitched text from messages."""
        texts = [msg.text for msg in messages if msg.text]
        if len(texts) == 1:
            return texts[0]
        elif len(texts) == 2:
            return f"{texts[0]} ... and {texts[1]}"
        else:
            return texts[0] + " ... " + " ... ".join(texts[1:-1]) + f" ... and {texts[-1]}"

    def check_for_continuation_keywords(self, message: Message) -> bool:
        """Check if message has continuation keywords."""
        continuation_words = ['also', 'and', 'plus', 'furthermore', 'moreover']
        text = message.text.lower() if message.text else ''
        return any(word in text for word in continuation_words)

    def force_stitch_for_chat(self, chat_id: int) -> None:
        """Force stitch messages for a chat."""
        self.stitch_messages(chat_id)

    def get_stitch_stats(self) -> Dict[str, Any]:
        """Get stitching statistics."""
        return {
            'pending_chats': len(self.pending_messages),
            'total_pending_messages': sum(len(msgs) for msgs in self.pending_messages.values()),
            'stitch_timeout': self.stitch_timeout,
            'max_stitch_length': self.max_stitch_length
        }

    def run_workflow(self, updates: List[Update]) -> None:
        """Run the workflow on a list of updates."""
        for update in updates:
            self.process_update(update)
            time.sleep(0.1)  # Small delay

    def example_usage(self) -> None:
        """Example of using the message stitching workflow."""
        # Simulate messages that should be stitched
        messages = [
            Message(message_id=1, date=int(time.time()), chat={'id': 123, 'type': 'private'}, text="First part"),
            Message(message_id=2, date=int(time.time()), chat={'id': 123, 'type': 'private'}, text="Second part"),
            Message(message_id=3, date=int(time.time()), chat={'id': 123, 'type': 'private'}, text="Third part")
        ]
        for msg in messages:
            update = Update(update_id=msg.message_id, message=msg)
            self.process_update(update)
            time.sleep(1)  # Simulate time between messages
