"""Workflow package aggregating orchestrated engagement strategies."""
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
from .workflow_suite import WORKFLOW_REGISTRY

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
