"""
Scheduled Messaging Workflow for Telegram Bot.

This workflow sends messages at scheduled times using existing Telegram API endpoints.
"""

import time
import threading
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.telegram.api.telegram_api import TelegramBotAPI, Message


class ScheduledMessagingWorkflow:
    """Workflow for sending scheduled messages."""

    def __init__(self, bot: TelegramBotAPI):
        self.bot = bot
        self.scheduled_messages: List[Dict[str, Any]] = []
        self.running = False
        self.thread = None

    def schedule_message(self, chat_id: int, text: str, delay_seconds: int) -> None:
        """Schedule a message to be sent after a delay."""
        send_time = time.time() + delay_seconds
        self.scheduled_messages.append({
            'chat_id': chat_id,
            'text': text,
            'send_time': send_time,
            'sent': False
        })

    def schedule_daily_message(self, chat_id: int, text: str, hour: int, minute: int = 0) -> None:
        """Schedule a daily message at a specific time."""
        now = datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        delay = (target_time - now).total_seconds()
        self.schedule_message(chat_id, text, int(delay))

    def start_scheduler(self) -> None:
        """Start the scheduling thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()

    def stop_scheduler(self) -> None:
        """Stop the scheduling thread."""
        self.running = False
        if self.thread:
            self.thread.join()

    def _run_scheduler(self) -> None:
        """Internal method to run the scheduler loop."""
        while self.running:
            current_time = time.time()
            for msg in self.scheduled_messages[:]:
                if not msg['sent'] and current_time >= msg['send_time']:
                    try:
                        self.bot.send_message(msg['chat_id'], msg['text'])
                        msg['sent'] = True
                    except Exception as e:
                        print(f"Failed to send scheduled message: {e}")
            time.sleep(1)  # Check every second

    def send_immediate_message(self, chat_id: int, text: str) -> Message:
        """Send a message immediately."""
        return self.bot.send_message(chat_id, text)

    def send_reminder(self, chat_id: int, text: str, minutes: int) -> None:
        """Send a reminder after specified minutes."""
        self.schedule_message(chat_id, text, minutes * 60)

    def broadcast_message(self, chat_ids: List[int], text: str) -> List[Message]:
        """Broadcast a message to multiple chats."""
        messages = []
        for chat_id in chat_ids:
            try:
                msg = self.bot.send_message(chat_id, text)
                messages.append(msg)
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")
        return messages

    def get_pending_messages(self) -> List[Dict[str, Any]]:
        """Get list of pending scheduled messages."""
        return [msg for msg in self.scheduled_messages if not msg['sent']]

    def clear_sent_messages(self) -> None:
        """Remove sent messages from the list."""
        self.scheduled_messages = [msg for msg in self.scheduled_messages if not msg['sent']]

    def run_workflow_example(self) -> None:
        """Example of running the workflow."""
        # Schedule a message in 10 seconds
        self.schedule_message(123, "This is a scheduled message!", 10)
        # Schedule a daily message at 9 AM
        self.schedule_daily_message(123, "Good morning!", 9, 0)
        # Start the scheduler
        self.start_scheduler()
        # Let it run for a while (in real use, keep running)
        time.sleep(15)
        self.stop_scheduler()
