"""Posting workflow worker utilities."""
from __future__ import annotations

import datetime
import json
import logging
import os
import threading
from typing import Iterable, List, Optional, Sequence

import schedule
from apscheduler.schedulers.background import BackgroundScheduler
from pushbullet import Pushbullet

from AWS import keys
from app import messages, posting

logger = logging.getLogger(__name__)

_SCHEDULER = BackgroundScheduler()
_SCHEDULE_THREAD_NAME = "groupme-schedule-runner"


def _resolve_pushbullet_key() -> str:
    """Return the Pushbullet key from env vars or AWS secrets."""
    pushbullet_key = os.environ.get("PUSH_BULLET")
    if pushbullet_key:
        return pushbullet_key

    token_obj = json.loads(keys.get_secret("PUSH_BULLET"))
    resolved_key = token_obj.get("PUSH_BULLET")
    if not resolved_key:
        raise RuntimeError("Pushbullet key could not be resolved from secrets store.")
    logger.info("Pushbullet key loaded from secrets store.")
    return resolved_key


def _create_pushbullet_client() -> Pushbullet:
    """Instantiate a Pushbullet client using the configured key."""
    key = _resolve_pushbullet_key()
    return Pushbullet(key)


def _schedule_post_times(
    filtered_bots: Sequence[dict],
    new_message: str,
    uploaded_images: Optional[Sequence[str]],
    post_times: Sequence[str],
) -> None:
    for post_time in post_times:
        logger.info("Scheduling daily post at %s", post_time)
        schedule.every().day.at(post_time).do(
            posting.send_message_to_groups,
            filtered_bots,
            new_message,
            uploaded_images,
        )

        time_obj = datetime.datetime.strptime(post_time, "%H:%M").time()
        date_obj = datetime.date.today()
        combined_time = datetime.datetime.combine(date_obj, time_obj)
        _SCHEDULER.add_job(
            posting.send_message_to_groups,
            "cron",
            hour=combined_time.hour,
            minute=combined_time.minute,
            args=[filtered_bots, new_message, uploaded_images],
        )


def _schedule_post_interval(
    filtered_bots: Sequence[dict],
    new_message: str,
    uploaded_images: Optional[Sequence[str]],
    hours: int,
) -> None:
    logger.info("Scheduling interval post every %s hour(s)", hours)
    _SCHEDULER.add_job(
        posting.send_message_to_groups,
        "interval",
        hours=hours,
        args=[filtered_bots, new_message, uploaded_images],
    )


def _upload_images(image_urls: Iterable[str]) -> List[str]:
    uploaded_images: List[str] = []
    for image in image_urls:
        uploaded_url = posting.upload_image_to_groupme(image)
        if uploaded_url:
            uploaded_images.append(uploaded_url)
        else:
            logger.warning("Failed to upload image %s", image)
    return uploaded_images


def _dispatch_message_configuration(
    filtered_bots: Sequence[dict],
    message_config: dict,
    *,
    production: bool,
) -> None:
    message_text = message_config.get("message", "")
    duration = message_config.get("duration")
    post_times = message_config.get("times") or []
    images = message_config.get("images") or []

    uploaded_images = _upload_images(images) if images else None

    if production:
        posting.send_message_to_groups(filtered_bots, message_text, uploaded_images)

    if duration:
        thread = threading.Thread(
            target=_schedule_post_interval,
            name=f"interval-{message_text[:8]}",
            args=(filtered_bots, message_text, uploaded_images, duration),
            daemon=True,
        )
        thread.start()

    if post_times:
        thread = threading.Thread(
            target=_schedule_post_times,
            name=f"times-{message_text[:8]}",
            args=(filtered_bots, message_text, uploaded_images, post_times),
            daemon=True,
        )
        thread.start()


def _start_schedule_loop(pushbullet_client: Pushbullet) -> None:
    """Start the scheduler and the blocking schedule loop."""
    _SCHEDULER.start()
    _SCHEDULER.print_jobs()

    def run_pending() -> None:
        while True:
            try:
                schedule.run_pending()
            except (KeyboardInterrupt, SystemExit) as exc:
                _SCHEDULER.shutdown()
                pushbullet_client.push_note("Group Me -", "App Crashed", str(exc))
                break

    runner = threading.Thread(target=run_pending, name=_SCHEDULE_THREAD_NAME, daemon=True)
    runner.start()
    runner.join()


def run_posting_workflow(filtered_bots: Sequence[dict], production: bool = True) -> None:
    """Run the posting workflow for the provided bots."""
    pushbullet_client = _create_pushbullet_client()

    for message in messages.message_duration_data:
        _dispatch_message_configuration(filtered_bots, message, production=production)

    _start_schedule_loop(pushbullet_client)
