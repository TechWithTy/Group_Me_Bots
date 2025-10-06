"""Aggregated registry mirroring GroupMe and Telegram workflow suites."""
from __future__ import annotations

from .base import WorkflowContext, WorkflowKPI, WorkflowResult
from .commerce_workflows import SignalCommerceEscrowWorkflow
from .data_management_workflows import SignalBackupComplianceWorkflow
from .engagement_workflows import (
    SignalAutoLikeFeedbackWorkflow,
    SignalContentQualityWorkflow,
    SignalEmergencyResponseWorkflow,
)
from .growth_workflows import SignalInviteAmplificationWorkflow
from .integration_workflows import SignalCrossNetworkRelayWorkflow
from .message_workflows import (
    SignalContentEchoWorkflow,
    SignalMessageStitchingWorkflow,
    SignalSecurityModerationWorkflow,
)
from .tracking_workflows import SignalRealTimeInsightsWorkflow

WORKFLOW_REGISTRY = {
    workflow.name: workflow
    for workflow in (
        SignalAutoLikeFeedbackWorkflow(),
        SignalContentQualityWorkflow(),
        SignalEmergencyResponseWorkflow(),
        SignalMessageStitchingWorkflow(),
        SignalSecurityModerationWorkflow(),
        SignalContentEchoWorkflow(),
        SignalBackupComplianceWorkflow(),
        SignalCrossNetworkRelayWorkflow(),
        SignalRealTimeInsightsWorkflow(),
        SignalInviteAmplificationWorkflow(),
        SignalCommerceEscrowWorkflow(),
    )
}

__all__ = [
    "SignalAutoLikeFeedbackWorkflow",
    "SignalContentQualityWorkflow",
    "SignalEmergencyResponseWorkflow",
    "SignalMessageStitchingWorkflow",
    "SignalSecurityModerationWorkflow",
    "SignalContentEchoWorkflow",
    "SignalBackupComplianceWorkflow",
    "SignalCrossNetworkRelayWorkflow",
    "SignalRealTimeInsightsWorkflow",
    "SignalInviteAmplificationWorkflow",
    "SignalCommerceEscrowWorkflow",
    "WorkflowContext",
    "WorkflowKPI",
    "WorkflowResult",
    "WORKFLOW_REGISTRY",
]
