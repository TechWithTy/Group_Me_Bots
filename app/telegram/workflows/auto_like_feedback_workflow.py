"""
Auto Like Feedback Workflow for Telegram Bot.

This workflow automatically likes messages and provides feedback,
similar to GroupMe's AutoLikeFeedbackWorkflow.
"""

import time
import random
from typing import Dict, Any, List, Optional
from app.telegram.api.telegram_api import TelegramBotAPI, Update, Message


class AutoLikeFeedbackWorkflow:
    """Workflow for automatic liking and feedback on messages."""

    title = "Telegram Auto-Like Feedback"
    description = "React to positive conversations and acknowledge community feedback automatically."
    goal = "Surface appreciation and maintain conversational momentum by engaging with high-sentiment messages."
    kpis = [
        {
            "name": "positive_feedback_responses",
            "target": ">=80%",
            "description": "Share of positive sentiment messages that receive a tailored response.",
        },
        {
            "name": "reaction_rate",
            "target": ">=30%",
            "description": "Percentage of processed messages that receive an emoji reaction.",
        },
        {
            "name": "duplicate_processing_rate",
            "target": "<=1%",
            "description": "Rate of duplicate message handling due to idempotency issues.",
        },
    ]

    def __init__(self, bot: TelegramBotAPI, like_probability: float = 0.3, feedback_keywords: Optional[List[str]] = None):
        self.bot = bot
        self.like_probability = like_probability  # Probability to "like" (react) to messages
        self.feedback_keywords = feedback_keywords or ['great', 'awesome', 'thanks', 'good job', 'well done']
        self.processed_messages = set()  # To avoid duplicate processing

    def process_update(self, update: Update) -> None:
        """Process an incoming update for auto-like and feedback."""
        if update.message and update.message.message_id not in self.processed_messages:
            self.processed_messages.add(update.message.message_id)
            self.handle_message(update.message)

    def handle_message(self, message: Message) -> None:
        """Handle a message for liking and feedback."""
        if message.text:
            self.check_for_feedback(message)
            if random.random() < self.like_probability:
                self.react_to_message(message)

    def check_for_feedback(self, message: Message) -> None:
        """Check if message contains feedback keywords and respond."""
        text = message.text.lower()
        for keyword in self.feedback_keywords:
            if keyword in text:
                responses = ["Glad you liked it!", "Thanks for the feedback!", "Appreciate it!"]
                response = random.choice(responses)
                self.bot.send_message(message.chat.id, response)
                break

    def react_to_message(self, message: Message) -> None:
        """React to a message (simulate like with a response)."""
        reactions = ["👍", "❤️", "Nice!", "Cool!", "Great!"]
        reaction = random.choice(reactions)
        self.bot.send_message(message.chat.id, reaction)

    def auto_respond_to_positive_messages(self, message: Message) -> None:
        """Auto-respond to positive messages."""
        if message.text and any(pos in message.text.lower() for pos in ['love', 'amazing', 'fantastic']):
            self.bot.send_message(message.chat.id, "I'm glad you're enjoying it!")

    def track_message_sentiment(self, message: Message) -> str:
        """Track message sentiment (placeholder for ML analysis)."""
        # Placeholder for sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'love']
        negative_words = ['bad', 'terrible', 'hate']
        text = message.text.lower() if message.text else ''
        if any(word in text for word in positive_words):
            return 'positive'
        elif any(word in text for word in negative_words):
            return 'negative'
        return 'neutral'

    def provide_feedback_based_on_sentiment(self, message: Message) -> None:
        """Provide feedback based on sentiment."""
        sentiment = self.track_message_sentiment(message)
        if sentiment == 'positive':
            self.bot.send_message(message.chat.id, "Happy to hear that!")
        elif sentiment == 'negative':
            self.bot.send_message(message.chat.id, "Sorry to hear that. How can I help?")

    def run_workflow(self, updates: List[Update]) -> None:
        """Run the workflow on a list of updates."""
        for update in updates:
            self.process_update(update)
            time.sleep(0.1)  # Small delay

    def get_stats(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        return {
            'processed_messages': len(self.processed_messages),
            'like_probability': self.like_probability,
            'feedback_keywords': self.feedback_keywords
        }
