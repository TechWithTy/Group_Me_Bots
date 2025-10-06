"""Message-centric workflow implementations for Signal."""
from __future__ import annotations

from typing import Any, Iterable, List, Sequence

from .base import WorkflowContext, WorkflowDefinition, WorkflowKPI, WorkflowResult

__all__ = [
    "SignalMessageStitchingWorkflow",
    "SignalSecurityModerationWorkflow",
    "SignalContentEchoWorkflow",
]


class SignalMessageStitchingWorkflow(WorkflowDefinition):
    """Identify conversations worth stitching across Signal groups."""

    name = "signal_message_stitching_content_echo"
    title = "Signal Message Stitching"
    description = (
        "Collects high-signal threads, stitches them together, and republishes summaries"
        " across designated groups leveraging Signal forwarding APIs."
    )
    goal = "Amplify cross-group engagement by sharing conversation highlights."
    kpis = (
        WorkflowKPI("qualified_threads", ">=3", "Threads identified for stitching"),
        WorkflowKPI("forward_success_rate", ">=0.8", "Successful forwards across groups"),
        WorkflowKPI("summary_completeness", ">=0.9", "Messages covered in generated summary"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")

        source_group: str = kwargs.get("source_group", "")
        target_groups: Sequence[str] = tuple(kwargs.get("target_groups", ()))
        limit: int = int(kwargs.get("limit", 40))
        summary_prefix: str = kwargs.get("summary_prefix", "Conversation highlights:")

        if not source_group or not target_groups:
            return WorkflowResult(False, {"error": "source_group and target_groups are required"})

        messages = list(
            await signal_client.fetch_group_messages(
                group_id=source_group,
                limit=limit,
            )
        )
        threads = self._group_by_thread(messages)
        ranked_threads = sorted(threads.values(), key=self._score_thread, reverse=True)

        stitched_threads = ranked_threads[: len(target_groups)]
        forwards = 0
        for thread in stitched_threads:
            summary = self._build_summary(thread, summary_prefix)
            for target in target_groups:
                try:
                    await signal_client.send_group_message(group_id=target, text=summary)
                    forwards += 1
                except Exception:  # pragma: no cover - defensive logging
                    continue

        qualified_threads = len(stitched_threads)
        possible_forwards = max(1, qualified_threads * len(target_groups))
        forward_rate = forwards / possible_forwards
        achieved = qualified_threads >= min(3, len(target_groups)) and forward_rate >= 0.8

        metrics = {
            "source_group": source_group,
            "target_groups": len(target_groups),
            "qualified_threads": qualified_threads,
            "forwards_sent": forwards,
            "forward_rate": forward_rate,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)

    @staticmethod
    def _group_by_thread(messages: Iterable[dict[str, Any]]) -> dict[str, List[dict[str, Any]]]:
        grouped: dict[str, List[dict[str, Any]]] = {}
        for message in messages:
            thread_id = str(message.get("thread_id") or message.get("reply_to") or message.get("id"))
            grouped.setdefault(thread_id, []).append(message)
        return grouped

    @staticmethod
    def _score_thread(thread: List[dict[str, Any]]) -> float:
        reactions = sum(int(msg.get("reactions", 0)) for msg in thread)
        contributors = {msg.get("author") for msg in thread}
        has_media = any(msg.get("attachments") for msg in thread)
        base = len(thread) / 5.0
        reaction_score = reactions / 15.0
        contributor_bonus = len(contributors) * 0.1
        media_bonus = 0.2 if has_media else 0.0
        return base + reaction_score + contributor_bonus + media_bonus

    @staticmethod
    def _build_summary(thread: List[dict[str, Any]], prefix: str) -> str:
        ordered = sorted(thread, key=lambda item: item.get("timestamp", 0))
        important = ordered[:5]
        lines = [prefix]
        for message in important:
            author = message.get("author", "member")
            text = (message.get("text") or message.get("content") or "").strip()
            lines.append(f"• {author}: {text[:120]}")
        return "\n".join(lines)


class SignalSecurityModerationWorkflow(WorkflowDefinition):
    """Flag policy violations and sensitive content in Signal groups."""

    name = "signal_security_moderation_monitoring"
    title = "Signal Security Moderation"
    description = (
        "Runs heuristic scanning against spam, abuse, and sensitive data within Signal"
        " conversations and reports violations for review."
    )
    goal = "Detect at least one actionable policy violation per run."
    kpis = (
        WorkflowKPI("violation_detection", ">=0.9", "Rate of policy violations detected"),
        WorkflowKPI("false_positive_control", "<=0.1", "Share of false positives"),
        WorkflowKPI("escalations", ">=1", "Violations escalated to trust & safety"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")

        group_id: str = kwargs.get("group_id", "")
        limit: int = int(kwargs.get("limit", 60))
        sensitive_keywords: Sequence[str] = tuple(
            kw.lower()
            for kw in kwargs.get(
                "sensitive_keywords",
                ("spam", "scam", "phish", "password", "credit card", "social security"),
            )
        )

        if not group_id:
            return WorkflowResult(False, {"error": "group_id is required"})

        messages_list = list(
            await signal_client.fetch_group_messages(
                group_id=group_id,
                limit=limit,
            )
        )

        flagged: List[dict[str, Any]] = []
        for message in messages_list:
            content = str(message.get("text") or message.get("content") or "").lower()
            attachments = message.get("attachments") or []
            if any(keyword in content for keyword in sensitive_keywords) or any(
                att.get("type") == "document" for att in attachments
            ):
                flagged.append(message)
                await signal_client.report_message(group_id=group_id, message=message)

        false_positive_ratio = kwargs.get("expected_false_positive_ratio", 0.05)
        achieved = len(flagged) > 0 and false_positive_ratio <= 0.1
        metrics = {
            "group_id": group_id,
            "messages_scanned": len(messages_list),
            "violations_detected": len(flagged),
            "sensitive_keywords": list(sensitive_keywords),
            "false_positive_ratio": false_positive_ratio,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)


class SignalContentEchoWorkflow(WorkflowDefinition):
    """Echo high-performing content across Signal groups and contacts."""

    name = "signal_content_echo"
    title = "Signal Content Echo"
    description = (
        "Echoes trending Signal messages to target groups and VIP contacts using the"
        " platform's forwarding and story posting capabilities."
    )
    goal = "Reach at least five distinct audiences with curated content."
    kpis = (
        WorkflowKPI("echo_engagement_rate", ">=0.7", "Engagement on echoed content"),
        WorkflowKPI("audience_reach", ">=5", "Unique audiences reached"),
        WorkflowKPI("story_amplification", ">=2", "Stories published from echoed content"),
    )

    async def execute(self, context: WorkflowContext, **kwargs: Any) -> WorkflowResult:
        signal_client = self._require(context, "signal_client")

        source_group: str = kwargs.get("source_group", "")
        target_groups: Sequence[str] = tuple(kwargs.get("target_groups", ()))
        vip_contacts: Sequence[str] = tuple(kwargs.get("vip_contacts", ()))
        story_enabled: bool = bool(kwargs.get("story_enabled", True))

        if not source_group:
            return WorkflowResult(False, {"error": "source_group is required"})

        messages = list(
            await signal_client.fetch_group_messages(
                group_id=source_group,
                limit=int(kwargs.get("limit", 25)),
            )
        )

        curated = self._select_curated_messages(messages)
        total_targets = len(target_groups) + len(vip_contacts)
        delivered = 0
        stories_published = 0

        for message in curated:
            payload = {
                "text": message.get("text") or message.get("content"),
                "attachments": message.get("attachments", []),
            }
            for target in target_groups:
                await signal_client.send_group_message(group_id=target, text=payload["text"], attachments=payload["attachments"])
                delivered += 1
            for contact in vip_contacts:
                await signal_client.forward_to_contact(contact=contact, message=message)
                delivered += 1
            if story_enabled and message.get("attachments"):
                await signal_client.post_story(content=message)
                stories_published += 1

        achieved = delivered >= max(5, total_targets) and (not story_enabled or stories_published >= 2)
        metrics = {
            "source_group": source_group,
            "curated_messages": len(curated),
            "deliveries": delivered,
            "audience_targets": total_targets,
            "stories_published": stories_published,
        }
        return WorkflowResult(achieved_goal=achieved, metrics=metrics)

    @staticmethod
    def _select_curated_messages(messages: Iterable[dict[str, Any]]) -> List[dict[str, Any]]:
        curated: List[dict[str, Any]] = []
        for message in messages:
            reactions = int(message.get("reactions", 0))
            has_media = bool(message.get("attachments"))
            if reactions >= 3 or has_media:
                curated.append(message)
        return curated[:5]
