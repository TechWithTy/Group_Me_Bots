"""
Workflow Suite for Telegram Bot.

This suite runs multiple Telegram workflows together,
similar to GroupMe's workflow_suite.py.
"""

import time
import threading
from typing import Dict, Any, List, Optional
from app.telegram.api.telegram_api import TelegramBotAPI, Update
from app.telegram.workflows.integration_workflows import IntegrationWorkflows


class WorkflowSuite:
    """Suite to run multiple Telegram workflows."""

    def __init__(self, bot: TelegramBotAPI, enabled_workflows: Optional[List[str]] = None):
        self.bot = bot
        self.integration = IntegrationWorkflows(bot)
        self.enabled_workflows = enabled_workflows or [
            'message_handling',
            'member_management',
            'scheduled_messaging',
            'media_processing',
            'auto_like_feedback',
            'adaptive_frequency',
            'message_stitching'
        ]
        self.running = False
        self.suite_thread = None

    def start_suite(self) -> None:
        """Start the workflow suite."""
        if not self.running:
            self.running = True
            self.suite_thread = threading.Thread(target=self._run_suite, daemon=True)
            self.suite_thread.start()

    def stop_suite(self) -> None:
        """Stop the workflow suite."""
        self.running = False
        if self.suite_thread:
            self.suite_thread.join()

    def _run_suite(self) -> None:
        """Internal method to run the suite loop."""
        while self.running:
            # In a real implementation, fetch updates here
            # For example: updates = self.bot.get_updates()
            # self.integration.run_all_workflows(updates)
            time.sleep(1)  # Polling interval

    def run_once(self, updates: List[Update]) -> None:
        """Run the suite once on a list of updates."""
        self.integration.run_all_workflows(updates)

    def get_suite_stats(self) -> Dict[str, Any]:
        """Get statistics from the suite."""
        return {
            'enabled_workflows': self.enabled_workflows,
            'running': self.running,
            'workflow_stats': self.integration.get_workflow_stats()
        }

    def add_workflow(self, workflow_name: str) -> bool:
        """Add a workflow to the suite."""
        if workflow_name not in self.integration.workflows:
            return False
        if workflow_name not in self.enabled_workflows:
            self.enabled_workflows.append(workflow_name)
        return True

    def remove_workflow(self, workflow_name: str) -> bool:
        """Remove a workflow from the suite."""
        if workflow_name in self.enabled_workflows:
            self.enabled_workflows.remove(workflow_name)
            return True
        return False

    def schedule_message_across_workflows(self, chat_id: int, message: str, delay: int) -> None:
        """Schedule a message using the scheduled workflow."""
        self.integration.schedule_integrated_message(chat_id, message, delay)

    def example_suite_run(self) -> None:
        """Example of running the workflow suite."""
        # Simulate updates
        updates = [
            Update(update_id=1, message={'message_id': 1, 'date': int(time.time()), 'chat': {'id': 123, 'type': 'private'}, 'text': 'Hello'}),
            Update(update_id=2, message={'message_id': 2, 'date': int(time.time()), 'chat': {'id': 123, 'type': 'private'}, 'text': 'How are you?'}),
        ]
        self.run_once(updates)
        print("Suite example completed.")
