"""Workflow orchestration suite for Discord bot."""
from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .base import WorkflowContext, WorkflowResult
from .message_stitching_workflow import MessageStitchingWorkflow
from .engagement_workflows import (
    AutoLikeFeedbackWorkflow,
    ContentQualityRelevanceWorkflow,
    AutomatedCustomerSupportWorkflow,
    EmergencyResponseWorkflow,
)
from .message_workflows import (
    MessageStitchingWorkflow as MessageStitchingWorkflow2,
    SecurityModerationWorkflow,
    ContentEchoWorkflow,
)
from .commerce_workflows import CommerceIntentWorkflow
from .growth_workflows import GhostInvitationWorkflow, ServerGrowthWorkflow
from .tracking_workflows import RealTimeSubscriptionWorkflow, AnalyticsWorkflow, MessageAnalyticsWorkflow
from .data_management_workflows import DataBackupWorkflow, DataCleanupWorkflow, DataMigrationWorkflow
from .media_processing_workflows import MediaProcessingWorkflow, ImageOptimizationWorkflow, VideoProcessingWorkflow, FileUploadWorkflow
from .member_management_workflows import MemberManagementWorkflow, RoleManagementWorkflow, MemberOnboardingWorkflow, MemberRetentionWorkflow
from .notification_workflows import NotificationWorkflow, ScheduledMessagingWorkflow, AnnouncementWorkflow, ReminderWorkflow

logger = logging.getLogger(__name__)

@dataclass
class WorkflowSuiteResult:
    """Result of running the entire workflow suite."""
    workflow_results: Dict[str, WorkflowResult]
    overall_success: bool
    total_metrics: Dict[str, Any]


class DiscordWorkflowSuite:
    """Orchestrates all Discord workflows."""

    def __init__(self, discord_client):
        self.discord_client = discord_client
        self.workflows = {}

        # Initialize workflows
        self._initialize_workflows()

    def _initialize_workflows(self):
        """Initialize all available workflows."""
        # Message stitching workflow
        self.workflows['message_stitching'] = MessageStitchingWorkflow(self.discord_client)

        # Engagement workflows
        self.workflows['auto_like_feedback'] = AutoLikeFeedbackWorkflow()
        self.workflows['content_quality_relevance'] = ContentQualityRelevanceWorkflow()
        self.workflows['automated_customer_support'] = AutomatedCustomerSupportWorkflow()
        self.workflows['emergency_response'] = EmergencyResponseWorkflow()

        # Message workflows
        self.workflows['message_stitching_content_echo'] = MessageStitchingWorkflow2()
        self.workflows['security_moderation'] = SecurityModerationWorkflow()
        self.workflows['content_echo'] = ContentEchoWorkflow()

        # Commerce workflows
        self.workflows['commerce_intent_detection'] = CommerceIntentWorkflow()

        # Growth workflows
        self.workflows['ghost_invitation'] = GhostInvitationWorkflow()
        self.workflows['server_growth'] = ServerGrowthWorkflow()

        # Tracking workflows
        self.workflows['real_time_subscription'] = RealTimeSubscriptionWorkflow()
        self.workflows['analytics_collection'] = AnalyticsWorkflow()
        self.workflows['message_analytics'] = MessageAnalyticsWorkflow()

        # Data management workflows
        self.workflows['data_backup'] = DataBackupWorkflow()
        self.workflows['data_cleanup'] = DataCleanupWorkflow()
        self.workflows['data_migration'] = DataMigrationWorkflow()

        # Media processing workflows
        self.workflows['media_processing'] = MediaProcessingWorkflow()
        self.workflows['image_optimization'] = ImageOptimizationWorkflow()
        self.workflows['video_processing'] = VideoProcessingWorkflow()
        self.workflows['file_upload_management'] = FileUploadWorkflow()

        # Member management workflows
        self.workflows['member_management'] = MemberManagementWorkflow()
        self.workflows['role_management'] = RoleManagementWorkflow()
        self.workflows['member_onboarding'] = MemberOnboardingWorkflow()
        self.workflows['member_retention'] = MemberRetentionWorkflow()

        # Notification workflows
        self.workflows['notification_system'] = NotificationWorkflow()
        self.workflows['scheduled_messaging'] = ScheduledMessagingWorkflow()
        self.workflows['announcement_distribution'] = AnnouncementWorkflow()
        self.workflows['reminder_system'] = ReminderWorkflow()

    async def run_workflow_suite(self, context: WorkflowContext, workflow_configs: Optional[Dict[str, Dict[str, Any]]] = None) -> WorkflowSuiteResult:
        """Run all configured workflows with provided configurations."""
        if workflow_configs is None:
            workflow_configs = {}

        results = {}
        overall_success = True

        for workflow_name, workflow in self.workflows.items():
            try:
                config = workflow_configs.get(workflow_name, {})
                logger.info(f"Running workflow: {workflow_name}")

                result = await workflow.execute(context, **config)
                results[workflow_name] = result

                if not result.achieved_goal:
                    overall_success = False
                    logger.warning(f"Workflow {workflow_name} failed to achieve goal")

            except Exception as e:
                logger.error(f"Error running workflow {workflow_name}: {e}")
                results[workflow_name] = WorkflowResult(achieved_goal=False, metrics={"error": str(e)})
                overall_success = False

        # Aggregate metrics
        total_metrics = self._aggregate_metrics(results)

        return WorkflowSuiteResult(
            workflow_results=results,
            overall_success=overall_success,
            total_metrics=total_metrics
        )

    def _aggregate_metrics(self, results: Dict[str, WorkflowResult]) -> Dict[str, Any]:
        """Aggregate metrics from all workflow results."""
        total_metrics = {
            'total_workflows': len(results),
            'successful_workflows': sum(1 for r in results.values() if r.achieved_goal),
            'failed_workflows': sum(1 for r in results.values() if not r.achieved_goal),
        }

        # Aggregate specific metrics
        for workflow_name, result in results.items():
            for metric_name, metric_value in result.metrics.items():
                if metric_name not in total_metrics:
                    total_metrics[metric_name] = 0
                if isinstance(metric_value, (int, float)):
                    total_metrics[metric_name] += metric_value

        return total_metrics

    async def run_specific_workflow(self, workflow_name: str, context: WorkflowContext, **kwargs) -> WorkflowResult:
        """Run a specific workflow by name."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        workflow = self.workflows[workflow_name]
        return await workflow.execute(context, **kwargs)

    def get_available_workflows(self) -> List[str]:
        """Get list of available workflow names."""
        return list(self.workflows.keys())

    def get_workflow_info(self, workflow_name: str) -> Dict[str, Any]:
        """Get information about a specific workflow."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        workflow = self.workflows[workflow_name]
        return {
            'name': workflow.name,
            'goal': workflow.goal,
            'kpis': [kpi.__dict__ for kpi in workflow.kpis],
        }

    async def run_guild_workflows(self, guild_id: int, context: WorkflowContext) -> WorkflowSuiteResult:
        """Run workflows specifically configured for a Discord guild."""
        # Configure workflows for guild-specific execution
        workflow_configs = {
            'server_growth': {'guild_id': guild_id},
            'analytics_collection': {'guild_id': guild_id},
            'data_backup': {'guild_id': guild_id},
            'data_cleanup': {'guild_id': guild_id},
            'member_management': {'guild_id': guild_id},
            'role_management': {'guild_id': guild_id},
            'member_onboarding': {'guild_id': guild_id},
            'member_retention': {'guild_id': guild_id},
            'announcement_distribution': {'guild_id': guild_id},
        }

        return await self.run_workflow_suite(context, workflow_configs)

    async def run_message_stitching_for_channel(self, channel_id: int, context: WorkflowContext) -> WorkflowResult:
        """Run message stitching workflow for a specific channel."""
        return await self.run_specific_workflow(
            'message_stitching',
            context,
            channel_id=channel_id
        )

    async def run_engagement_workflows_for_channel(self, channel_id: int, context: WorkflowContext) -> Dict[str, WorkflowResult]:
        """Run all engagement-related workflows for a channel."""
        engagement_workflows = [
            'auto_like_feedback',
            'content_quality_relevance',
            'automated_customer_support',
            'emergency_response'
        ]

        results = {}
        for workflow_name in engagement_workflows:
            config = {'channel_id': channel_id}
            if workflow_name == 'auto_like_feedback':
                config['message_ids'] = []  # Would need to be populated with actual message IDs
            elif workflow_name == 'content_echo':
                config.update({
                    'source_channel_id': channel_id,
                    'target_channel_ids': []  # Would need target channels
                })

            results[workflow_name] = await self.run_specific_workflow(workflow_name, context, **config)

        return results


__all__ = ["DiscordWorkflowSuite", "WorkflowSuiteResult"]
