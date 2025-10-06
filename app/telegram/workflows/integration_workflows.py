"""
Integration Workflows for Telegram Bot.

This workflow integrates multiple Telegram workflows together,
similar to GroupMe's integration_workflows.py.
"""

import time
from typing import Dict, Any, List
from app.telegram.api.telegram_api import TelegramBotAPI, Update
from app.telegram.workflows.message_handling_workflow import MessageHandlingWorkflow
from app.telegram.workflows.member_management_workflow import MemberManagementWorkflow
from app.telegram.workflows.scheduled_messaging_workflow import ScheduledMessagingWorkflow
from app.telegram.workflows.media_processing_workflow import MediaProcessingWorkflow
from app.telegram.workflows.auto_like_feedback_workflow import AutoLikeFeedbackWorkflow
from app.telegram.workflows.adaptive_frequency_workflow import AdaptiveFrequencyWorkflow
from app.telegram.workflows.message_stitching_workflow import MessageStitchingWorkflow


class IntegrationWorkflows:
    """Integrates multiple Telegram workflows."""

    def __init__(self, bot: TelegramBotAPI):
        self.bot = bot
        self.workflows = {
            'message_handling': MessageHandlingWorkflow(bot),
            'member_management': MemberManagementWorkflow(bot),
            'scheduled_messaging': ScheduledMessagingWorkflow(bot),
            'media_processing': MediaProcessingWorkflow(bot),
            'auto_like_feedback': AutoLikeFeedbackWorkflow(bot),
            'adaptive_frequency': AdaptiveFrequencyWorkflow(bot),
            'message_stitching': MessageStitchingWorkflow(bot),
        }

    def process_update(self, update: Update) -> None:
        """Process an update through all integrated workflows."""
        for workflow_name, workflow in self.workflows.items():
            try:
                workflow.process_update(update)
            except Exception as e:
                print(f"Error in {workflow_name}: {e}")

    def run_all_workflows(self, updates: List[Update]) -> None:
        """Run all workflows on a list of updates."""
        for update in updates:
            self.process_update(update)
            time.sleep(0.05)  # Small delay between updates

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get statistics from all workflows."""
        stats = {}
        for name, workflow in self.workflows.items():
            if hasattr(workflow, 'get_stats'):
                stats[name] = workflow.get_stats()
            elif hasattr(workflow, 'get_frequency_stats'):
                stats[name] = workflow.get_frequency_stats()
            elif hasattr(workflow, 'get_stitch_stats'):
                stats[name] = workflow.get_stitch_stats()
        return stats

    def get_workflow_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Expose descriptive metadata for each registered workflow."""

        metadata: Dict[str, Dict[str, Any]] = {}
        for name, workflow in self.workflows.items():
            metadata[name] = {
                'title': getattr(workflow, 'title', ''),
                'description': getattr(workflow, 'description', ''),
                'goal': getattr(workflow, 'goal', ''),
                'kpis': getattr(workflow, 'kpis', []),
            }
        return metadata

    def enable_workflow(self, workflow_name: str) -> bool:
        """Enable a specific workflow."""
        if workflow_name in self.workflows:
            return True  # In a real implementation, add enable/disable logic
        return False

    def disable_workflow(self, workflow_name: str) -> bool:
        """Disable a specific workflow."""
        if workflow_name in self.workflows:
            return True  # Placeholder
        return False

    def schedule_integrated_message(self, chat_id: int, message: str, delay: int) -> None:
        """Schedule a message using the scheduled messaging workflow."""
        self.workflows['scheduled_messaging'].schedule_message(chat_id, message, delay)

    def run_example_integration(self) -> None:
        """Example of running integrated workflows."""
        # Simulate updates
        updates = [
            Update(update_id=1, message={'message_id': 1, 'date': int(time.time()), 'chat': {'id': 123, 'type': 'private'}, 'text': '/start'}),
            Update(update_id=2, message={'message_id': 2, 'date': int(time.time()), 'chat': {'id': 123, 'type': 'private'}, 'text': 'Hello bot!'}),
        ]
        self.run_all_workflows(updates)
        print("Integration example completed.")
