"""End-to-end style tests for data management and integration workflows."""
from __future__ import annotations

import asyncio
from workflows.base import WorkflowContext
from workflows.data_management_workflows import DataBackupRecoveryWorkflow
from workflows.integration_workflows import MultiPlatformIntegrationWorkflow


def test_data_backup_recovery_workflow_reports_backup_metrics() -> None:
    """Workflow should report backup metrics and meet success criteria."""

    context = WorkflowContext()
    workflow = DataBackupRecoveryWorkflow()

    result = asyncio.run(
        workflow.execute(
            context,
            group_ids=["g1", "g2", "g3"],
            backup_type="incremental",
            test_recovery=True,
            minimum_groups=3,
        )
    )

    assert result.achieved_goal is True
    assert result.metrics == {
        "groups_backed_up": 3,
        "backup_type": "incremental",
        "recovery_tested": True,
        "successful_backups": 3,
    }


def test_multi_platform_integration_workflow_computes_sync_results() -> None:
    """Workflow should compute sync metrics across integrated platforms."""

    context = WorkflowContext()
    workflow = MultiPlatformIntegrationWorkflow()

    result = asyncio.run(
        workflow.execute(
            context,
            platforms=["discord", "slack", "teams"],
            data_types=["messages", "users"],
            minimum_sync_success_rate=0.99,
        )
    )

    assert result.achieved_goal is True
    assert result.metrics["platforms_integrated"] == 3
    assert result.metrics["data_types_synced"] == 2
    assert result.metrics["total_sync_operations"] == 6
    assert 0.99 <= result.metrics["sync_success_rate"] <= 1.0
    assert result.metrics["consistency_score"] == 0.97
    assert result.metrics["integration_uptime"] == 0.998
