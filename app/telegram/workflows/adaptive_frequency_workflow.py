"""
Adaptive Frequency Workflow for Telegram Bot.

This workflow adjusts message frequency based on activity levels,
similar to GroupMe's AdaptiveFrequencyWorkflow.
"""

import time
from typing import Dict, Any, List, Optional
from collections import defaultdict
from app.telegram.api.telegram_api import TelegramBotAPI, Update, Message


class AdaptiveFrequencyWorkflow:
    """Workflow for adapting message frequency based on chat activity."""

    def __init__(self, bot: TelegramBotAPI, base_interval: int = 60, max_interval: int = 300, min_interval: int = 10):
        self.bot = bot
        self.base_interval = base_interval  # Base time between messages (seconds)
        self.max_interval = max_interval  # Maximum interval
        self.min_interval = min_interval  # Minimum interval
        self.current_interval = base_interval
        self.message_counts = defaultdict(int)  # Track messages per chat
        self.last_message_times = defaultdict(float)  # Last message time per chat
        self.activity_threshold = 5  # Messages per hour to increase frequency

    def process_update(self, update: Update) -> None:
        """Process an incoming update to adjust frequency."""
        if update.message:
            self.update_frequency(update.message)

    def update_frequency(self, message: Message) -> None:
        """Update frequency based on message activity."""
        chat_id = message.chat.id
        now = time.time()

        # Update message count and time
        self.message_counts[chat_id] += 1
        self.last_message_times[chat_id] = now

        # Calculate activity level
        time_window = 3600  # 1 hour
        recent_messages = sum(1 for t in self.last_message_times.values() if now - t <= time_window)

        # Adjust interval based on activity
        if recent_messages > self.activity_threshold:
            self.current_interval = max(self.min_interval, self.current_interval - 10)
        else:
            self.current_interval = min(self.max_interval, self.current_interval + 5)

    def should_send_message(self, chat_id: int) -> bool:
        """Check if it's time to send a message based on current interval."""
        now = time.time()
        last_time = self.last_message_times.get(chat_id, 0)
        return (now - last_time) >= self.current_interval

    def send_adaptive_message(self, chat_id: int, base_message: str) -> bool:
        """Send a message if frequency allows."""
        if self.should_send_message(chat_id):
            try:
                self.bot.send_message(chat_id, f"{base_message} (Interval: {self.current_interval}s)")
                self.last_message_times[chat_id] = time.time()
                return True
            except Exception as e:
                print(f"Failed to send message: {e}")
                return False
        return False

    def get_adaptive_reminder(self, chat_id: int) -> Optional[str]:
        """Get a reminder message based on activity."""
        activity = self.message_counts.get(chat_id, 0)
        if activity > 10:
            return "Chat is very active! Keeping up the pace."
        elif activity > 5:
            return "Moderate activity. Adjusting frequency."
        else:
            return "Low activity. Slowing down messages."

    def reset_for_chat(self, chat_id: int) -> None:
        """Reset frequency tracking for a specific chat."""
        self.message_counts.pop(chat_id, None)
        self.last_message_times.pop(chat_id, None)

    def get_frequency_stats(self) -> Dict[str, Any]:
        """Get current frequency statistics."""
        return {
            'current_interval': self.current_interval,
            'base_interval': self.base_interval,
            'max_interval': self.max_interval,
            'min_interval': self.min_interval,
            'total_chats_tracked': len(self.message_counts),
            'message_counts': dict(self.message_counts)
        }

    def run_workflow(self, updates: List[Update]) -> None:
        """Run the workflow on a list of updates."""
        for update in updates:
            self.process_update(update)
            time.sleep(0.1)  # Small delay

    def example_usage(self) -> None:
        """Example of using the adaptive frequency workflow."""
        # Simulate processing updates
        for i in range(10):
            # Simulate an update
            update = Update(update_id=i, message=Message(message_id=i, date=int(time.time()), chat={'id': 123, 'type': 'private'}))
            self.process_update(update)
            if i % 3 == 0:
                self.send_adaptive_message(123, "Adaptive message")
            time.sleep(1)
