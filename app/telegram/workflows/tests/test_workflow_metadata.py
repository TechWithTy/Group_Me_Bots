"""Metadata coverage tests for Telegram workflows."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.telegram.workflows.message_handling_workflow import MessageHandlingWorkflow
from app.telegram.workflows.member_management_workflow import MemberManagementWorkflow
from app.telegram.workflows.scheduled_messaging_workflow import ScheduledMessagingWorkflow
from app.telegram.workflows.media_processing_workflow import MediaProcessingWorkflow
from app.telegram.workflows.auto_like_feedback_workflow import AutoLikeFeedbackWorkflow
from app.telegram.workflows.adaptive_frequency_workflow import AdaptiveFrequencyWorkflow
from app.telegram.workflows.message_stitching_workflow import MessageStitchingWorkflow


@pytest.mark.parametrize(
    "workflow_cls",
    [
        MessageHandlingWorkflow,
        MemberManagementWorkflow,
        ScheduledMessagingWorkflow,
        MediaProcessingWorkflow,
        AutoLikeFeedbackWorkflow,
        AdaptiveFrequencyWorkflow,
        MessageStitchingWorkflow,
    ],
)
def test_telegram_workflows_expose_metadata(workflow_cls):
    """Ensure each Telegram workflow advertises metadata fields."""

    bot = MagicMock()
    workflow = workflow_cls(bot)

    assert isinstance(workflow.title, str) and workflow.title.strip()
    assert isinstance(workflow.description, str) and workflow.description.strip()
    assert isinstance(workflow.goal, str) and workflow.goal.strip()

    assert isinstance(workflow.kpis, list) and workflow.kpis
    for kpi in workflow.kpis:
        assert {"name", "target", "description"}.issubset(kpi.keys())
        assert all(isinstance(kpi[key], str) and kpi[key].strip() for key in ("name", "target", "description"))
