"""Aggregate access to orchestrated workflows and registry helpers."""
from __future__ import annotations

from .base import WorkflowContext, WorkflowKPI, WorkflowResult
from .commerce_workflows import CommerceIntentWorkflow
from .engagement_workflows import (
    AdaptiveFrequencyWorkflow,
    OnboardingFunnelWorkflow,
    ProgressivePermissionWorkflow,
    SoftOptInWorkflow,
)
from .growth_workflows import GhostInvitationWorkflow
from .message_workflows import AutoLikeFeedbackWorkflow, MessageStitchingWorkflow
from .tracking_workflows import ContentMiningWorkflow, RealTimeSubscriptionWorkflow

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
    )
}

__all__ = [
    "AdaptiveFrequencyWorkflow",
    "AutoLikeFeedbackWorkflow",
    "CommerceIntentWorkflow",
    "ContentMiningWorkflow",
    "GhostInvitationWorkflow",
    "MessageStitchingWorkflow",
    "OnboardingFunnelWorkflow",
    "ProgressivePermissionWorkflow",
    "RealTimeSubscriptionWorkflow",
    "SoftOptInWorkflow",
    "WorkflowContext",
    "WorkflowKPI",
    "WorkflowResult",
    "WORKFLOW_REGISTRY",
]
