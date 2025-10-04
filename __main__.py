"""CLI entry point for the GroupMe posting workflow."""
from __future__ import annotations

from app import bots
from workers import run_posting_workflow


def main() -> None:
    """Load bots and start the posting workflow."""
    bot_inventory = bots.get_bots()
    filtered_bots = bots.filter_bots(bot_inventory)
    run_posting_workflow(filtered_bots)


if __name__ == "__main__":
    main()
