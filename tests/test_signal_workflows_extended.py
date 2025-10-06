"""Extended regression tests for the Signal workflow suite."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

import pytest

from app.signal.workflows.base import WorkflowContext
from app.signal.workflows.commerce_workflows import SignalCommerceEscrowWorkflow
from app.signal.workflows.data_management_workflows import (
    SignalBackupComplianceWorkflow,
)
from app.signal.workflows.growth_workflows import SignalInviteAmplificationWorkflow
from app.signal.workflows.integration_workflows import (
    SignalCrossNetworkRelayWorkflow,
)
from app.signal.workflows.tracking_workflows import SignalRealTimeInsightsWorkflow
from app.signal.workflows.workflow_suite import WORKFLOW_REGISTRY
from tests.signal_workflow_stubs import (
    StubIntegrationsClient,
    StubPaymentsClient,
    StubSignalClient,
    StubStorageClient,
    StubTrackingWorker,
)


def _messages() -> List[Dict[str, Any]]:
    return [
        {
            "id": "m1",
            "group_id": "g1",
            "text": "Great launch update",
            "reactions": 4,
            "expires_in": 12,
        },
        {
            "id": "m2",
            "group_id": "g1",
            "text": "Need urgent help",
            "reactions": 1,
            "expires_in": 24,
        },
    ]


@pytest.fixture()
def extended_context() -> WorkflowContext:
    return WorkflowContext(
        signal_client=StubSignalClient(_messages()),
        storage_client=StubStorageClient(),
        integrations_client=StubIntegrationsClient(),
        payments_client=StubPaymentsClient(),
        tracking_worker=StubTrackingWorker(),
    )


@pytest.mark.asyncio()
async def test_backup_compliance_workflow_stores_group_backups(extended_context: WorkflowContext) -> None:
    workflow = SignalBackupComplianceWorkflow()

    result = await workflow.execute(
        extended_context,
        group_ids=["g1"],
        retention_hours=24,
        compliance_threshold=0.5,
    )

    assert result.achieved_goal is True
    assert extended_context.storage_client.backups
    assert result.metrics["retention_compliance"] >= 0.5


@pytest.mark.asyncio()
async def test_cross_network_relay_workflow_relays_payloads(extended_context: WorkflowContext) -> None:
    workflow = SignalCrossNetworkRelayWorkflow()

    result = await workflow.execute(
        extended_context,
        payloads=[{"id": "m1", "text": "Hello"}],
        target_platforms=["telegram", "groupme"],
    )

    assert result.achieved_goal is True
    assert len(extended_context.integrations_client.relayed) == 2


@pytest.mark.asyncio()
async def test_realtime_insights_workflow_collects_metrics(extended_context: WorkflowContext) -> None:
    workflow = SignalRealTimeInsightsWorkflow()

    result = await workflow.execute(extended_context, group_id="g1", timeframe_hours=12)

    assert result.achieved_goal is True
    assert extended_context.tracking_worker.collected


@pytest.mark.asyncio()
async def test_invite_amplification_workflow_handles_contacts(extended_context: WorkflowContext) -> None:
    workflow = SignalInviteAmplificationWorkflow()

    result = await workflow.execute(
        extended_context,
        group_id="g1",
        candidate_contacts=["c1", "c2"],
    )

    assert result.achieved_goal is True
    invites = [action for action in extended_context.signal_client.actions if action[0] == "invite"]
    assert len(invites) == 2


@pytest.mark.asyncio()
async def test_commerce_escrow_workflow_processes_orders(extended_context: WorkflowContext) -> None:
    workflow = SignalCommerceEscrowWorkflow()

    result = await workflow.execute(
        extended_context,
        orders=[{"order_id": "o1", "amount": 15.0}],
        auto_release=True,
    )

    assert result.achieved_goal is True
    assert extended_context.payments_client.invoices
    assert extended_context.payments_client.escrow_releases


def test_signal_workflow_registry_contains_full_suite() -> None:
    expected = {
        "signal_auto_like_feedback",
        "signal_content_quality_relevance",
        "signal_emergency_response",
        "signal_message_stitching_content_echo",
        "signal_security_moderation_monitoring",
        "signal_content_echo",
        "signal_data_backup_compliance",
        "signal_cross_network_relay",
        "signal_realtime_insights",
        "signal_invite_amplification",
        "signal_commerce_escrow",
    }

    assert expected.issubset(WORKFLOW_REGISTRY.keys())
