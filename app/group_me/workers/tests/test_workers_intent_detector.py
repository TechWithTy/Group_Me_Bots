"""Tests for the intent detection worker."""
import asyncio

from ..workers.intent_detector import IntentPlan, run_intent_detection_workflow


def test_run_intent_detection_workflow_detects_commerce_intent():
    plan = IntentPlan(message_text="I want to buy a gift")

    report = asyncio.run(run_intent_detection_workflow(plan))

    assert report.intent == "commerce"
    assert report.confidence > 0.5


def test_run_intent_detection_workflow_defaults_to_chitchat():
    plan = IntentPlan(message_text="How was your day?")

    report = asyncio.run(run_intent_detection_workflow(plan))

    assert report.intent == "chitchat"
