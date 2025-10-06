"""Data management workflows for Signal retention and compliance."""
from __future__ import annotations

from typing import Any, Sequence

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = ["SignalBackupComplianceWorkflow"]


class SignalBackupComplianceWorkflow(WorkflowDefinition):
    """Archive Signal conversations while respecting disappearing timer policies."""

    name = "signal_data_backup_compliance"
    title = "Signal Backup & Compliance"
    description = (
        "Streams group conversations into compliant storage, tagging disappearing "
        "message timers and sealed-sender metadata for retention audits."
    )
    goal = "Maintain compliant backups for every configured Signal group."
    kpis = (
        WorkflowKPI("backup_coverage", "100%", "Groups backed up during the run"),
        WorkflowKPI("ephemeral_capture", ">=0.7", "Ephemeral messages captured before expiry"),
        WorkflowKPI("retention_alignment", ">=0.8", "Timers aligned with policy"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        storage_client = self._require(context, "storage_client")
        signal_client = self._require(context, "signal_client")

        group_ids: Sequence[str] = tuple(kwargs.get("group_ids", ()))
        if not group_ids:
            return WorkflowResult(False, {"error": "group_ids are required"})

        retention_hours: int = int(kwargs.get("retention_hours", 24))
        compliance_threshold: float = float(kwargs.get("compliance_threshold", 0.8))
        message_limit: int = int(kwargs.get("message_limit", 50))
        include_media: bool = bool(kwargs.get("include_media", True))

        total_messages = 0
        compliant_messages = 0

        for group_id in group_ids:
            messages = await signal_client.fetch_group_messages(group_id=group_id, limit=message_limit)
            await storage_client.store_backup(
                group_id=group_id,
                retention_hours=retention_hours,
                include_media=include_media,
                message_count=len(messages),
            )
            total_messages += len(messages)
            compliant_messages += sum(
                1
                for message in messages
                if int(message.get("expires_in", retention_hours)) <= retention_hours
            )

        retention_compliance = (
            compliant_messages / total_messages if total_messages else 1.0
        )
        achieved = len(group_ids) > 0 and retention_compliance >= compliance_threshold

        metrics = {
            "groups_processed": len(group_ids),
            "retention_hours": retention_hours,
            "include_media": include_media,
            "messages_sampled": total_messages,
            "retention_compliance": retention_compliance,
            "compliance_threshold": compliance_threshold,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)
