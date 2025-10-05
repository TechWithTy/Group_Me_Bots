"""Worker package for background workflows."""
from __future__ import annotations

from importlib import import_module
from typing import Any

from .commands import CommandPlan, run_command_workflow
from .commerce import CommercePlan, CommerceReport, run_commerce_workflow
from .intent_detector import IntentPlan, IntentReport, run_intent_detection_workflow
from .moderation import ModerationPlan, ModerationReport, run_moderation_workflow

__all__ = [
    "CommandPlan",
    "CommercePlan",
    "CommerceReport",
    "IntentPlan",
    "IntentReport",
    "ModerationPlan",
    "ModerationReport",
    "run_command_workflow",
    "run_commerce_workflow",
    "run_intent_detection_workflow",
    "run_moderation_workflow",
    "run_posting_workflow",
]


def __getattr__(name: str) -> Any:
    if name == "run_posting_workflow":
        module = import_module("workers.posting")
        return getattr(module, name)
    raise AttributeError(name)

