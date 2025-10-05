"""Aggregate access to orchestrated workflows and registry helpers."""
from __future__ import annotations

from .base import WorkflowContext, WorkflowKPI, WorkflowResult
from .commerce_workflows import CommerceIntentWorkflow
from .data_management_workflows import DataBackupRecoveryWorkflow
from .engagement_workflows import (
    ABTestingWorkflow,
    AdaptiveFrequencyWorkflow,
    CommunityHealthMonitoringWorkflow,
    OnboardingFunnelWorkflow,
    PersonalizationEngineWorkflow,
    ProgressivePermissionWorkflow,
    SoftOptInWorkflow,
    UserRetentionChurnPreventionWorkflow,
)
from .growth_workflows import GhostInvitationWorkflow
from .integration_workflows import MultiPlatformIntegrationWorkflow
from .message_workflows import (
    AutoLikeFeedbackWorkflow,
    AutomatedCustomerSupportWorkflow,
    ContentQualityRelevanceWorkflow,
    EmergencyResponseWorkflow,
    MessageStitchingWorkflow,
    SecurityModerationWorkflow,
)
from .tracking_workflows import (
    AdvancedAnalyticsInsightsWorkflow,
    AnalyticsReportingWorkflow,
    ContentMiningWorkflow,
    PerformanceMonitoringWorkflow,
    RealTimeSubscriptionWorkflow,
)

WORKFLOW_REGISTRY = {
    workflow.name: workflow
    for workflow in (
        MessageStitchingWorkflow(),
        AdaptiveFrequencyWorkflow(),
        SoftOptInWorkflow(),
        RealTimeSubscriptionWorkflow(),
        GhostInvitationWorkflow(),
        AutoLikeFeedbackWorkflow(),
        ContentMiningWorkflow(),
        CommerceIntentWorkflow(),
        OnboardingFunnelWorkflow(),
        ProgressivePermissionWorkflow(),
        AnalyticsReportingWorkflow(),
        SecurityModerationWorkflow(),
        PerformanceMonitoringWorkflow(),
        ABTestingWorkflow(),
        DataBackupRecoveryWorkflow(),
        UserRetentionChurnPreventionWorkflow(),
        ContentQualityRelevanceWorkflow(),
        AutomatedCustomerSupportWorkflow(),
        EmergencyResponseWorkflow(),
        CommunityHealthMonitoringWorkflow(),
        AdvancedAnalyticsInsightsWorkflow(),
        PersonalizationEngineWorkflow(),
        MultiPlatformIntegrationWorkflow(),
    )
}

__all__ = [
    "ABTestingWorkflow",
    "AdaptiveFrequencyWorkflow",
    "AdvancedAnalyticsInsightsWorkflow",
    "AnalyticsReportingWorkflow",
    "AutoLikeFeedbackWorkflow",
    "AutomatedCustomerSupportWorkflow",
    "CommerceIntentWorkflow",
    "CommunityHealthMonitoringWorkflow",
    "ContentMiningWorkflow",
    "ContentQualityRelevanceWorkflow",
    "DataBackupRecoveryWorkflow",
    "EmergencyResponseWorkflow",
    "GhostInvitationWorkflow",
    "MessageStitchingWorkflow",
    "MultiPlatformIntegrationWorkflow",
    "OnboardingFunnelWorkflow",
    "PerformanceMonitoringWorkflow",
    "PersonalizationEngineWorkflow",
    "ProgressivePermissionWorkflow",
    "RealTimeSubscriptionWorkflow",
    "SecurityModerationWorkflow",
    "SoftOptInWorkflow",
    "UserRetentionChurnPreventionWorkflow",
    "WorkflowContext",
    "WorkflowKPI",
    "WorkflowResult",
    "WORKFLOW_REGISTRY",
]
