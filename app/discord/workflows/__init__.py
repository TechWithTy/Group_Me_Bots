"""Discord workflows package."""

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult
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
from .workflow_suite import DiscordWorkflowSuite, WorkflowSuiteResult

__all__ = [
    "WorkflowContext",
    "WorkflowDefinition",
    "WorkflowKPI",
    "WorkflowResult",
    "MessageStitchingWorkflow",
    "AutoLikeFeedbackWorkflow",
    "ContentQualityRelevanceWorkflow",
    "AutomatedCustomerSupportWorkflow",
    "EmergencyResponseWorkflow",
    "MessageStitchingWorkflow2",
    "SecurityModerationWorkflow",
    "ContentEchoWorkflow",
    "DiscordWorkflowSuite",
    "WorkflowSuiteResult",
]
